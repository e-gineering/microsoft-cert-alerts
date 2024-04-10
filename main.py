import os
import requests
import yaml
from datetime import datetime
import dotenv
from azure.communication.email import EmailClient

dotenv.load_dotenv()


def send_email(
    email_address: str, certification_title: str, days_until_expiration: int
):
    """
    Send an email to the given email address about the certification that is expiring soon
    :param email_address: The email address to send the email to
    :param certification_title: The title of the certification
    :param days_until_expiration: The number of days until the certification expires
    """
    print(
        f"Sending email to {email_address} about the certification {certification_title} that expires in {days_until_expiration} days"
    )

    try:
        connection_string = os.getenv("AZURE_COMMUNICATION_SERVICES_CONNECTION_STRING")
        sender_address = os.getenv("AZURE_COMMUNICATION_SERVICES_SENDER_ADDRESS")

        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": sender_address,
            "recipients": {
                "to": [{"address": email_address}],
            },
            "content": {
                "subject": f"{certification_title} expires in {days_until_expiration} days",
                "plainText": f"This is a reminder that your certification **{certification_title}** is expiring in {days_until_expiration} days.",
            },
        }

        client.begin_send(message).result()

    except Exception as ex:
        print(ex)


print("Parsing the certifications.yaml file")
config_file = yaml.load(open("certifications.yaml"), Loader=yaml.FullLoader)

users = config_file["users"]

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

        days_until_expiration = (
            certification_expiration_date - datetime.today().date()
        ).days

        print(
            f"Certification with the ID {credential_id} expires on {certification_expiration_date}, which is in {days_until_expiration} days"
        )

        if days_until_expiration < 60:
            send_email(email, certification_title, days_until_expiration)
        else:
            print(
                f"The certification {credential_id} expires in more than 60 days, so no email will be sent"
            )
