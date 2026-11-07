"""Schema, decimal and cross-field accounting checks."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from document_extractor.finance import parse_money, valid_cnpj
from document_extractor.schemas import FinancialDocument, Origin
from document_extractor.validation import validate_financial


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("R$ 1.234,56", "1234.56"),
        ("$1,234.56", "1234.56"),
        ("10,25", "10.25"),
        ("-1.25", "-1.25"),
        (Decimal("0.01"), "0.01"),
        (0, "0"),
    ],
)
def test_money(value: object, expected: str) -> None:
    assert parse_money(value) == Decimal(expected)


@pytest.mark.parametrize("value", ["x12", True, float("nan"), "1.2.3", "1,2,3"])
def test_bad_money(value: object) -> None:
    with pytest.raises(ValueError):
        parse_money(value)


def test_cnpj() -> None:
    assert valid_cnpj("11.222.333/0001-81")
    assert not valid_cnpj("11.222.333/0001-82")
    assert not valid_cnpj("00.000.000/0000-00")
    assert not valid_cnpj("123")
    assert not valid_cnpj("11-222-333-0001-81")


def test_date_and_missing() -> None:
    document = FinancialDocument(issue_date="15/01/2026")
    assert str(document.issue_date) == "2026-01-15"
    assert any(issue.code == "missing" for issue in validate_financial(document))


@pytest.mark.parametrize("date", ["2026-02-30", "31/11/2026", "nope"])
def test_bad_date(date: str) -> None:
    with pytest.raises(ValidationError):
        FinancialDocument(issue_date=date)


def test_strict_schema() -> None:
    with pytest.raises(ValidationError):
        FinancialDocument.model_validate({"not_a_field": 42})


def test_mismatched_totals_and_inference() -> None:
    document = FinancialDocument(
        document_type="invoice",
        issuer_name="FICTIONAL COMPANY",
        issue_date="2026-01-15",
        currency="BRL",
        subtotal="20",
        total="30",
        provenance={"total": Origin.INFERRED},
        items=[{"description": "Synthetic", "quantity": "2", "unit_price": "5", "total": "9"}],
    )
    codes = {issue.code for issue in validate_financial(document)}
    assert {"total_mismatch", "item_mismatch", "subtotal_mismatch", "inferred"} <= codes


def test_correct_calculations() -> None:
    document = FinancialDocument(
        document_type="receipt",
        issuer_name="Example",
        issue_date="2026-01-15",
        subtotal="150",
        discount="10",
        tax="5",
        surcharge="1",
        total="146",
        items=[{"description": "A", "quantity": "2", "unit_price": "75", "total": "150"}],
    )
    assert not validate_financial(document)


def test_invalid_quantity_and_negative() -> None:
    doc = FinancialDocument(items=[{"quantity": "0", "unit_price": "-3", "total": "-5"}])
    codes = {i.code for i in validate_financial(doc)}
    assert "invalid_quantity" in codes
    assert "negative_amount" in codes
