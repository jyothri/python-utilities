import argparse
import requests
import os
from utils.helpers import parse_certificates, format_certificates_as_html_table
from utils.email_sender import send_email
from datetime import datetime, timedelta, timezone

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process certificate file and send email for expiring certificates.")
    parser.add_argument("file_path", type=str, help="Path to the input file containing certificate details")
    args = parser.parse_args()

    # Use the provided file path
    file_path = args.file_path
    certificates = parse_certificates(file_path)
    
    # Get the current date with UTC timezone and calculate the 10-day threshold
    current_date = datetime.now(timezone.utc)
    threshold_date = current_date + timedelta(days=10)
    
    # Filter certificates expiring within the next 10 days
    expiring_soon = [
        cert for cert in certificates 
        if datetime.strptime(cert.expiry_date, "%Y-%m-%d %H:%M:%S%z") <= threshold_date
    ]
    
    # Print the filtered certificates
    for cert in expiring_soon:
        print(cert.name, cert.expiry_date, cert.status)
    
# Prepare the email content
    if expiring_soon:
        api_key = os.getenv("PLUNK_API_KEY")  # Read the API key from an environment variable
        if not api_key:
            raise ValueError("API key not found. Please set the PLUNK_API_KEY environment variable.")
        
        recipient_email = "jyothri@gmail.com"  # Replace with the recipient's email
        subject = "Certificates Expiring Soon"
        body = "The following certificates are expiring soon:\n\n"
        body += format_certificates_as_html_table(expiring_soon)

        # Send the email
        try:
            response = send_email(api_key, recipient_email, subject, body)
            print("Email sent successfully:", response)
        except requests.exceptions.RequestException as e:
            print("Failed to send email:", e)