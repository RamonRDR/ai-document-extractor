"""Financial cross-checks are advisory, never invented corrections."""

from decimal import Decimal

from .finance import valid_cnpj
from .schemas import FinancialDocument, Issue, Origin

CENT = Decimal("0.01")


def _cents(value: Decimal) -> Decimal:
    return value.quantize(CENT)


def validate_financial(document: FinancialDocument) -> list[Issue]:
    issues: list[Issue] = []

    for field in ("document_type", "issuer_name", "issue_date", "total"):
        if getattr(document, field) is None:
            issues.append(Issue(code="missing", field=field, message="Field not identified"))

    if document.issuer_cnpj and not valid_cnpj(document.issuer_cnpj):
        issues.append(
            Issue(code="invalid_cnpj", field="issuer_cnpj", message="CNPJ check digits invalid")
        )

    for field in ("subtotal", "discount", "tax", "surcharge", "total"):
        value = getattr(document, field)
        if value is not None and value < 0:
            issues.append(Issue(code="negative_amount", field=field, message="Negative amount"))

    for index, item in enumerate(document.items):
        if item.quantity is not None and item.quantity <= 0:
            issues.append(
                Issue(
                    code="invalid_quantity",
                    field=f"items[{index}].quantity",
                    message="Quantity must be positive",
                )
            )
        if item.unit_price is not None and item.unit_price < 0:
            issues.append(
                Issue(
                    code="negative_amount",
                    field=f"items[{index}].unit_price",
                    message="Negative amount",
                )
            )
        if item.total is not None and item.total < 0:
            issues.append(
                Issue(
                    code="negative_amount", field=f"items[{index}].total", message="Negative amount"
                )
            )
        if item.quantity is not None and item.unit_price is not None and item.total is not None:
            if _cents(item.quantity * item.unit_price) != _cents(item.total):
                issues.append(
                    Issue(
                        code="item_mismatch",
                        field=f"items[{index}].total",
                        message="Quantity × unit price differs from item total",
                    )
                )

    totals = [item.total for item in document.items]
    if totals and all(value is not None for value in totals):
        items_sum = sum((value for value in totals if value is not None), Decimal(0))
        if document.subtotal is not None and _cents(items_sum) != _cents(document.subtotal):
            issues.append(
                Issue(
                    code="subtotal_mismatch",
                    field="subtotal",
                    message="Sum of items differs from subtotal",
                )
            )
        elif (
            document.subtotal is None
            and document.total is not None
            and all(getattr(document, name) is None for name in ("discount", "tax", "surcharge"))
            and _cents(items_sum) != _cents(document.total)
        ):
            issues.append(
                Issue(
                    code="total_mismatch", field="total", message="Sum of items differs from total"
                )
            )

    if document.subtotal is not None and document.total is not None:
        expected = (
            document.subtotal
            - (document.discount or Decimal(0))
            + (document.tax or Decimal(0))
            + (document.surcharge or Decimal(0))
        )
        if _cents(expected) != _cents(document.total):
            issues.append(
                Issue(
                    code="total_mismatch",
                    field="total",
                    message="Subtotal and adjustments do not match total",
                )
            )

    for field, origin in document.provenance.items():
        if origin == Origin.INFERRED:
            issues.append(
                Issue(code="inferred", field=field, message="Inferred value requires human review")
            )

    return issues
