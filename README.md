# Commercium ERPNext Integration

Connect your ERPNext account with Commercium platform.

## Features
- One-click connect
- Secure user authentication
- Auto onboarding

## Setup
Install from Frappe Cloud marketplace.

### Configuration
Add your Commercium secret key to `site_config.json`:
```json
{
  "commercium_secret_key": "your-secret-key-here"
}
```
Alternatively, set the `COMMERCIUM_SECRET_KEY` environment variable.