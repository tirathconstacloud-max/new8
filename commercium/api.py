import frappe
from frappe import _
import hashlib
import hmac
import json
import time
import os


def _get_secret_key() -> str:
    """Get Commercium secret key from site config or environment."""
    key = frappe.conf.get("commercium_secret_key") or os.environ.get("COMMERCIUM_SECRET_KEY")
    if not key or not isinstance(key, str):
        frappe.throw(
            _("Commercium secret key not configured. Add 'commercium_secret_key' to site_config.json or set COMMERCIUM_SECRET_KEY env var.")
        )
    return key


@frappe.whitelist()
def connect_to_commercium():
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)

    payload = {
        "email": user_doc.email,
        "full_name": user_doc.full_name,
        "site": frappe.local.site,
        "timestamp": int(time.time())
    }

    payload_str = json.dumps(payload, separators=(',', ':'))

    signature = hmac.new(
        _get_secret_key().encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()

    redirect_url = f"https://commercium.constacloud.com/erp/callback?data={payload_str}&sig={signature}"

    return redirect_url