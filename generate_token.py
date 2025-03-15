from google_auth_oauthlib.flow import InstalledAppFlow
import json

CREDENTIALS_FILE = "/home/faisal-ababs/Learn_Agent_Ai/Python_Pratice/credentials.json"
TOKEN_FILE = "/home/faisal-ababs/Learn_Agent_Ai/Python_Pratice/token.json"

# ✅ Define SCOPES properly
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",  # For sending emails
    "https://www.googleapis.com/auth/gmail.readonly"  # For reading emails
]

# Authenticate user
flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
creds = flow.run_local_server(port=0)

# Save token
with open(TOKEN_FILE, "w") as token:
    token.write(creds.to_json())

print("✅ Authentication successful! `token.json` has been generated.")
