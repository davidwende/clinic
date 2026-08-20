"""Field validation shared with the desktop app's rules.

validate_tz is imported from Database.dbFuncs (the canonical implementation,
per clinic/CLAUDE.md). validate_phone mirrors check_good_phone from
Application_Main/main.py -- that function lives in a PySide6-importing
module so it isn't reused directly here, but the rule is copied verbatim.
"""
from pyisemail import is_email

from Database.dbFuncs import validate_tz

__all__ = ["validate_tz", "validate_phone", "validate_email_address"]


def validate_phone(phone: str) -> bool:
    phone = phone.strip().replace('-', '')
    return len(phone) in (9, 10) and phone.isdigit() and phone[0] == '0'


def validate_email_address(email: str) -> bool:
    return bool(is_email(email))
