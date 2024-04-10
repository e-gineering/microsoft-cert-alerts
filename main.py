import requests
import yaml
from datetime import datetime

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
