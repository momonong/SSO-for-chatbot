from flask import session
import base64
import json


def clear_token():
    if "oauth_token" in session:
        del session["oauth_token"]


def decode_token(access_token):
    try:
        jwt_parts = access_token.split(".")
        if len(jwt_parts) != 3:
            raise ValueError("Invalid token format")
        payload_encoded = jwt_parts[1]
        payload_encoded += "=" * (4 - len(payload_encoded) % 4)
        payload_decoded = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_decoded)
        return payload
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return {}


def normalize_name(display_name, student_en_name):
    """
    Normalize the display name and student English name to ensure consistent formatting.
    """
    if student_en_name.lower() not in display_name.lower():
        full_name = f"{display_name} {student_en_name}"
    else:
        full_name = display_name
    return full_name