import frappe
from frappe.utils import get_url
from urllib.parse import urlencode

@frappe.whitelist()
def connect_to_commercium():
    try:
        # 1. Get site URL
        site_url = get_url()

        # 2. Get Settings (Singleton)
        settings = frappe.get_single("Commercium")

        # Prevent duplicate connection
        if settings.get("connected"):
            frappe.throw("Already connected to Commercium")

        # 3. Extract user details and API credentials
        user_email = None
        user_name = None
        api_key = None
        api_secret = None

        if frappe.session.user and frappe.session.user != "Guest":
            user = frappe.get_doc("User", frappe.session.user)
            user_email = user.email or user.name
            user_name = user.full_name or user.name

            api_key = user.api_key
            api_secret = user.get_password("api_secret")

            if not api_key:
                api_key = frappe.generate_hash(length=15)
                user.api_key = api_key

            if not api_secret:
                api_secret = frappe.generate_hash(length=30)
                user.api_secret = api_secret

            if not user.is_new():
                user.save(ignore_permissions=True)
                frappe.db.commit()
        else:
            frappe.throw("Must be logged in to connect to Commercium")

        # 4. Build redirect URL for GET with query params
        payload = {
            "site_url": site_url,
            "api_key": api_key,
            "api_secret": api_secret,
            "user_email": user_email,
            "user_name": user_name
        }
        frappe.logger().info("Building Commercium redirect URL with payload: {}".format(payload))
        redirect_url = "https://commercium.constacloud.com/external-login?{}".format(
            urlencode(payload)
        )

        return {
            "status": "success",
            "redirect_url": redirect_url
        }

    except frappe.ValidationError:
        raise
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Commercium Connection Error")
        frappe.throw("Something went wrong while connecting to Commercium")