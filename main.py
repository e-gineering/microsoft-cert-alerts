import os
import requests
import yaml
from datetime import datetime, timedelta
import dotenv
from azure.communication.email import EmailClient

dotenv.load_dotenv()

def today():
    """Wrapper for datetime.today() to make it easier to mock in tests."""
    return datetime.today()

def send_email(email_address: str, subject: str, message: str):
    """
    Send an email to the given email address
    :param email_address: The email address to send the email to
    :param subject: The subject of the email
    :param message: The message content of the email
    """
    print(f"Sending email to {email_address} with subject '{subject}'")

    try:
        connection_string = os.getenv("AZURE_COMMUNICATION_SERVICES_CONNECTION_STRING")
        sender_address = os.getenv("AZURE_COMMUNICATION_SERVICES_SENDER_ADDRESS")

        client = EmailClient.from_connection_string(connection_string)

        email_message = {
            "senderAddress": sender_address,
            "recipients": {
                "to": [{"address": email_address}],
            },
            "content": {
                "subject": subject,
                "html": message,
            },
        }

        client.begin_send(email_message).result()

    except Exception as ex:
        print(ex)

def generate_renewal_email_body(certification_title: str, expiration_date: str, certification_id: str) -> str:
    """
    Generate the email body for the certification renewal notification
    :param certification_title: The title of the certification
    :param expiration_date: The expiration date of the certification
    :param certification_id: The ID of the certification
    :return: The email body content
    """
    return (f"<p>Your certification <strong>{certification_title}</strong> is now eligible for renewal.</p>"
            f"<p>It expires on <strong>{expiration_date}</strong>.</p>"
            f"<p>You can view the certification details <a href='https://learn.microsoft.com/en-us/users/me/credentials?tab=credentials-tab&credentialId={certification_id}'>here</a>.</p>")

def generate_expiration_email_body(certification_title: str, days_until_expiration: int) -> str:
    """
    Generate the email body for the certification expiration notification
    :param certification_title: The title of the certification
    :param days_until_expiration: The number of days until the certification expires
    :return: The email body content
    """
    return f"This is a reminder that your certification **{certification_title}** is expiring in {days_until_expiration} days."

def is_weekend(date):
    return date.weekday() > 4

def main():
    print("Parsing the certifications.yaml file")
    with open("certifications.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)

    users = config["users"]

    # Iterate over the users array
    for user in users:
        email = user["email"]
        certifications = user["certifications"]

        for certification in certifications:
            credential_id = certification["credentialId"]
            print(f"Found certification with the id {credential_id} for the user {email}")

            # Hit the Microsoft Learn endpoint to get cert details
            endpoint = f"https://learn.microsoft.com/api/credentials/{credential_id}"
            response = requests.get(endpoint)

            certification_title = response.json()["title"]
            certification_expiration_date_raw: str = response.json()["expiresOn"]
            certification_expiration_date: datetime.date = datetime.strptime(
                certification_expiration_date_raw, "%Y-%m-%dT%H:%M:%S.%f%z"
            ).date()

            days_until_expiration = (certification_expiration_date - today().date()).days

            print(f"Certification with the ID {credential_id} expires on {certification_expiration_date}, which is in {days_until_expiration} days")

            if (days_until_expiration == 180 and not is_weekend(today().date())) or (days_until_expiration in [179, 178] and today().weekday() == 0):  # Monday
                subject = f"{certification_title} is eligible for renewal"
                message = generate_renewal_email_body(certification_title, str(certification_expiration_date), credential_id)
                send_email(email, subject, message)
            elif days_until_expiration <= 60:
                subject = f"{certification_title} expires in {days_until_expiration} days"
                message = generate_expiration_email_body(certification_title, days_until_expiration)
                send_email(email, subject, message)
            else:
                print(f"The certification {credential_id} expires in more than 60 days, so no email will be sent")

if __name__ == "__main__":
    main()
