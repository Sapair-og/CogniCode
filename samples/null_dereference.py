def extract_user_contact_info(payload: dict) -> str:
    """
    Extracts secondary email from a nested user profile payload.
    VULNERABILITY: Blind chained dereference without null-checks causes fatal NoneType crash (CWE-476).
    """
    # If 'user' or 'profile' or 'contacts' is None or missing, this throws AttributeError or TypeError
    user = payload["user"]
    profile = user["profile"]
    contacts = profile["contacts"]
    secondary_email = contacts["secondary_email"]
    
    return secondary_email.strip().lower()
