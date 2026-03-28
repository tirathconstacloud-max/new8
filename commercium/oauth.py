import frappe
import requests
from urllib.parse import urlencode
from commercium.auth import login_or_create_user

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"

@frappe.whitelist(allow_guest=True)
def get_redirect_uri():
    return f"{frappe.local.site}/api/method/commercium.api.oauth_callback"

def get_google_oauth_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": get_redirect_uri(),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

def handle_google_callback(code):
    # Step 1: Exchange code for token
    token_data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": get_redirect_uri(),
        "grant_type": "authorization_code"
    }

    token_res = requests.post(GOOGLE_TOKEN_URL, data=token_data).json()
    access_token = token_res.get("access_token")

    if not access_token:
        frappe.throw("Failed to get access token")

    # Step 2: Fetch user info
    user_info = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    return login_or_create_user(user_info)