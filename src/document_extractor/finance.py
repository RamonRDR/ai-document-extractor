"""Brazilian identifier and decimal parsing helpers."""

import re
from decimal import Decimal, InvalidOperation

# Bounded contracts prevent quantize overflow and abusive extreme precision.
MAX_INTEGER_DIGITS = 12
MAX_DECIMAL_PLACES = 6


def parse_money(value: object) -> Decimal | None:
    """Parse common BRL/US formatted amounts without float conversion."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError("Boolean is not a monetary value")
    if isinstance(value, Decimal):
        result = value
    elif isinstance(value, int):
        result = Decimal(value)
    elif isinstance(value, str):
        text = value.strip().replace("R$", "").replace("$", "").replace(" ", "")
        if not text:
            return None
        negative = text.startswith("-")
        if negative:
            text = text[1:]
        if len(text) > 40 or not text or any(char not in "0123456789,." for char in text):
            raise ValueError("Invalid monetary format")
        if "." in text and "," in text:
            if text.rfind(",") > text.rfind("."):
                text = text.replace(".", "").replace(",", ".")
            else:
                text = text.replace(",", "")
        elif "," in text:
            if text.count(",") > 1:
                raise ValueError("Ambiguous monetary format")
            text = text.replace(",", ".")
        elif text.count(".") > 1:
            raise ValueError("Ambiguous monetary format")
        try:
            result = Decimal(("-" if negative else "") + text)
        except InvalidOperation as exc:
            raise ValueError("Invalid monetary value") from exc
    else:
        raise ValueError("Use decimal strings for monetary amounts")
    if not result.is_finite():
        raise ValueError("Non-finite decimal value")
    if result.adjusted() >= MAX_INTEGER_DIGITS:
        raise ValueError("Decimal magnitude exceeds supported range")
    if result.as_tuple().exponent < -MAX_DECIMAL_PLACES:
        raise ValueError("Decimal precision exceeds six fractional places")
    return result


def valid_cnpj(cnpj: str) -> bool:
    if re.fullmatch(r"(?:[0-9]{14}|[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2})", cnpj) is None:
        return False
    digits = "".join(ch for ch in cnpj if ch.isdigit())
    if len(digits) != 14 or len(set(digits)) == 1:
        return False

    def check(values: str, weights: list[int]) -> int:
        remainder = sum(int(v) * w for v, w in zip(values, weights, strict=True)) % 11
        return 0 if remainder < 2 else 11 - remainder

    first = check(digits[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second = check(digits[:13], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return digits[12] == str(first) and digits[13] == str(second)
