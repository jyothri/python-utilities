import requests

def send_email(api_key, recipient_email, subject, body):
    """
    Sends an email using the Plunk API.

    Args:
        api_key (str): Your Plunk API key.
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.

    Returns:
        dict: The response from the Plunk API.
    """
    url = "https://api.useplunk.com/v1/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": recipient_email,
        "subject": subject,
        "body": body
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()