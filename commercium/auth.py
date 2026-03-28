import secrets
from typing import Any, Callable, cast

import frappe
from frappe import _

# Installed frappe types often omit db/get_doc shapes; cast keeps Pyright aligned with runtime.
_get_doc = cast(Callable[..., Any], frappe.get_doc)
_db = cast(Any, frappe).db


def login_or_create_user(user_info):
    email = (user_info.get("email") or "").strip()
    if not email:
        frappe.throw(_("Email not provided by OAuth provider"))

    if _db.exists("User", email):
        _get_doc("User", email)
    else:
        user_doc = _get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": user_info.get("given_name") or "",
                "last_name": user_info.get("family_name") or "",
                "enabled": 1,
                "new_password": secrets.token_urlsafe(32),
            }
        )
        user_doc.insert(ignore_permissions=True)

    cast(Any, frappe.local).login_manager.login_as(email)

    return {
        "status": "success",
        "user": email,
    }
