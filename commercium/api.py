from base64 import urlsafe_b64encode
import frappe
from frappe.utils import get_url
from cryptography.fernet import Fernet
import json
from datetime import datetime, timedelta, timezone
import requests
from pathlib import Path

# SECRET_KEY = "HdMMKF-LYzAcKK_fBX7JKQjuBUlYyOjgq0GcfwxHacI="
def _get_secret_key():
    """Load or create the Commercium secret key at runtime."""
    return generate_secret_key()


def _write_commercium_log(message, level="INFO"):
    """Write integration logs to dedicated site log files."""
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        line = f"[{timestamp}] [{level}] {message}\n"

        log_dirs = [
            Path(frappe.get_site_path("private", "logs", "commercium")),
            Path(frappe.get_site_path("logs", "commercium")),
        ]

        for log_dir in log_dirs:
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "external_connection.log"
            with log_file.open("a", encoding="utf-8") as handle:
                handle.write(line)
    except Exception:
        # Never break API flow because of log write failures.
        pass

@frappe.whitelist()
def after_install():
    try:
        secret_key = _get_secret_key()
        site_url = get_url()
        external_response = send_external_connection(secret_key, site_url)
        if external_response is None:
            frappe.throw("External connection response is empty")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Disconnect from Commercium Error")
        frappe.throw("Something went wrong while disconnecting from Commercium")

@frappe.whitelist()
def connect_to_commercium():
    try:
        secret_key = _get_secret_key()

        # 1. Get site URL
        site_url = get_url()

        external_response = send_external_connection(secret_key, site_url)
        if external_response is None:
            frappe.throw("External connection response is empty")

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

        payload = {
            "site_url": site_url,
            "api_key": api_key,
            "api_secret": api_secret,
            "user_email": user_email,
            "user_name": user_name,
            "platform": "erpnext",
            "expiration_time": (datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat(),
        }

        f = Fernet(secret_key)
        json_data = json.dumps(payload)
        encrypted = f.encrypt(json_data.encode())
        token = encrypted.decode()

        encoded_site_url = urlsafe_b64encode(site_url.encode("utf-8")).decode("utf-8")

        redirect_url = "https://commercium.constacloud.com/external-connection?event=signup&site_url={}&platform=ERPNEXT&token={}".format(
            encoded_site_url,
            token
        )

        return {
            "status": "success",
            "redirect_url": redirect_url
        }

    except frappe.ValidationError:
        raise
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Commercium Connection Error")
        _write_commercium_log(
            f"connect_to_commercium failed: {frappe.get_traceback()}",
            level="ERROR",
        )
        frappe.throw("Something went wrong while connecting to Commercium")

@frappe.whitelist()
def generate_secret_key():
    try:
        # Store secret key directly in Singles to avoid hard dependency
        # on a dedicated "Commercium Secret Key" DocType.
        rows = frappe.db.sql(
            """
            SELECT value
            FROM `tabSingles`
            WHERE doctype = %s AND field = %s
            LIMIT 1
            """,
            ("Commercium", "secret_key"),
            as_list=True,
        )

        if rows and rows[0][0]:
            existing_key = rows[0][0]
            try:
                Fernet(existing_key.encode())
                return existing_key
            except Exception:
                # If key format is invalid, rotate it.
                pass

        secret_key = Fernet.generate_key().decode()
        frappe.db.sql(
            """
            INSERT INTO `tabSingles` (`doctype`, `field`, `value`)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE `value` = VALUES(`value`)
            """,
            ("Commercium", "secret_key", secret_key),
        )
        frappe.db.commit()
        return secret_key
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Generate Secret Key Error")
        frappe.throw("Something went wrong while generating secret key")

@frappe.whitelist()
def send_external_connection(secret_key, site_url):
    try:
        url = "https://whk.co.in/register-external-app/"
        payload = {
            "site_url": site_url, 
            "secret_key": secret_key,
            "token": "QkRDWENITk9FbS9uZWd3bFNJckxqTmJCbWpGbUpJWk9sODZMbFIvaFNzYz0="
        }
        _write_commercium_log(
            f"Outgoing request to register-external-app for site_url={site_url}",
            level="INFO",
        )
        response = requests.post(url, timeout=20, json=payload)

        if response.status_code in (200, 201):
            if not response.text:
                return {"status": "success", "message": "External app registered successfully"}
            try:
                payload = response.json()
                return payload if payload is not None else {"status": "success"}
            except ValueError:
                return {"status": "success", "raw_response": response.text}

        error_message = f"External API call failed with status {response.status_code}"
        _write_commercium_log(
            f"Non-200 response status={response.status_code}, "
            f"body={response.text[:2000]}",
            level="ERROR",
        )
        if response.text:
            try:
                error_payload = response.json()
                error_message = (
                    error_payload.get("message")
                    or error_payload.get("error")
                    or error_payload.get("detail")
                    or str(error_payload)
                )
                if isinstance(error_message, str) and "success" in error_message.lower():
                    return {"status": "success", "message": error_message, "raw_response": error_payload}
            except ValueError:
                # Avoid exposing full HTML error pages in user-facing messages.
                if "Not Found" in response.text:
                    error_message = "External API endpoint not found (404). Please verify the integration URL."
                elif "success" in response.text.lower():
                    return {"status": "success", "message": response.text}
                else:
                    error_message = f"External API call failed with status {response.status_code}"

        frappe.throw(error_message)
    except requests.exceptions.RequestException as e:
        frappe.log_error(
            title="External Connection API Error",
            message=str(e)
        )
        _write_commercium_log(f"Request exception: {str(e)}", level="ERROR")
        frappe.throw(f"API Request Failed: {str(e)}")
