

import frappe
from commercium.oauth import get_google_oauth_url, handle_google_callback

@frappe.whitelist(allow_guest=True)
def login_with_google():
    return {
        "redirect_url": get_google_oauth_url()
    }

@frappe.whitelist(allow_guest=True)
def oauth_callback(code=None, state=None):
    return handle_google_callback(code)
