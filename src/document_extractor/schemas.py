"""Strict data contracts and explicit provenance indicators."""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .finance import parse_money


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Origin(StrEnum):
    EXTRACTED = "extracted"
    INFERRED = "inferred"
    MISSING = "missing"
    DEMO = "demo"


class Item(StrictModel):
    description: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    total: Decimal | None = None

    @field_validator("quantity", "unit_price", "total", mode="before")
    @classmethod
    def decimal_value(cls, value: object) -> Decimal | None:
        return parse_money(value)


class FinancialDocument(StrictModel):
    document_type: str | None = None
    issuer_name: str | None = None
    issuer_cnpj: str | None = None
    issue_date: date | None = None
    document_number: str | None = None
    currency: str | None = None
    subtotal: Decimal | None = None
    discount: Decimal | None = None
    tax: Decimal | None = None
    surcharge: Decimal | None = None
    total: Decimal | None = None
    items: list[Item] = Field(default_factory=list, max_length=100)
    provenance: dict[str, Origin] = Field(default_factory=dict)

    @field_validator("subtotal", "discount", "tax", "surcharge", "total", mode="before")
    @classmethod
    def decimal_value(cls, value: object) -> Decimal | None:
        return parse_money(value)

    @field_validator("issue_date", mode="before")
    @classmethod
    def normalized_date(cls, value: object) -> date | None:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            raise ValueError("Date must not contain a time")
        if isinstance(value, date):
            return value
        if not isinstance(value, str):
            raise ValueError("Date must be a string")
        if "/" in value:
            return datetime.strptime(value, "%d/%m/%Y").date()
        return date.fromisoformat(value)

    @field_validator("currency")
    @classmethod
    def normalized_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        currency = value.upper()
        if len(currency) != 3 or not currency.isalpha():
            raise ValueError("Currency must be a three-letter ISO code")
        return currency


class Issue(StrictModel):
    code: str
    field: str
    message: str
    severity: Literal["warning", "error"] = "warning"


class ExtractionResult(StrictModel):
    mode: Literal["demo", "openai"]
    document: FinancialDocument
    issues: list[Issue]
    needs_review: bool
    processing_ms: int = Field(ge=0)
    prompt_version: str = "v1"
    notice: str


class ReviewRequest(StrictModel):
    original: ExtractionResult
    corrected: FinancialDocument
    confirmed: bool = False


class ReviewResult(ReviewRequest):
    issues: list[Issue] = Field(default_factory=list)


class BatchEntry(StrictModel):
    index: int
    success: bool
    result: ExtractionResult | None = None
    error: str | None = None


class BatchResult(StrictModel):
    entries: list[BatchEntry]
    success_count: int
    failure_count: int
