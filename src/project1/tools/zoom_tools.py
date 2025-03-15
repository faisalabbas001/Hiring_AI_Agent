from email.mime.text import MIMEText
import smtplib
import requests
import os
import base64
import datetime
import time
from dotenv import load_dotenv

load_dotenv()

class   ZoomTools:
    def __init__(self):
        
        self.zoom_client_id = os.getenv("ZOOM_CLIENT_ID")
        self.zoom_client_secret = os.getenv("ZOOM_CLIENT_SECRET")
        self.zoom_account_id = os.getenv("ZOOM_ACCOUNT_ID")  
        self.zoom_user_id = os.getenv("ZOOM_USER_ID", "me") 

    def get_access_token(self):
        """
        Get an OAuth access token using 'account_credentials' grant type for Zoom API.
        """
        url = "https://zoom.us/oauth/token"
        
      
        credentials = f"{self.zoom_client_id}:{self.zoom_client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        payload = {
            "grant_type": "account_credentials",
            "account_id": self.zoom_account_id 
        }

        response = requests.post(url, headers=headers, data=payload)
        
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"❌ Error obtaining access token: {response.text}")
            return None

    def create_zoom_meeting(self, topic, start_time, duration=30):
        """
        Create a Zoom meeting and return the join URL.
        
        Parameters:
        - topic: The topic of the meeting.
        - start_time: The start time of the meeting in ISO 8601 format.
        - duration: The duration of the meeting in minutes (default is 30).
        
        Returns:
        - The join URL of the created meeting or None if there was an error.
        """
        url = f"https://api.zoom.us/v2/users/{self.zoom_user_id}/meetings"
        access_token = self.get_access_token()  
        
        if not access_token:
            print("❌ Failed to obtain access token.")
            return None

        headers = {
            "Authorization": f"Bearer {access_token}", 
            "Content-Type": "application/json"
        }
        payload = {
            "topic": topic,
            "type": 2, 
            "start_time": start_time, 
            "duration": duration,
            "timezone": "UTC",
            "agenda": "Job interview for hiring position"
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            meeting_details = response.json()
            return meeting_details.get("join_url")  
        else:
            print(f"❌ Error creating Zoom meeting: {response.text}")
            return None
    import smtplib
    def send_zoom_invite(self, candidate_email):
        """
        Send a Zoom invitation to the candidate via email.
        """
        if not candidate_email:
            print("❌ No recipient email address provided.")
            return None  

        
        current_time_utc = datetime.datetime.utcnow()
        meeting_start_time = current_time_utc + datetime.timedelta(hours=1)
        start_time_iso = meeting_start_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        meeting_link = self.create_zoom_meeting("Job Interview", start_time_iso)

        if meeting_link:
            subject = "Your Zoom Meeting Invitation"
            body = f"Dear Candidate,\n\nYou have been selected for an interview. Here is your Zoom meeting link: {meeting_link}\n\nBest regards,\nHR Team"
            self.send_email(candidate_email, subject, body)
            msg = MIMEText(body)
            msg['Subject'] = 'Your Application Status'
            msg['From'] = 'rai.faisalpasha2003@gmail.com'  
            msg['To'] = candidate_email

            print(f"📧 Attempting to send email to: {candidate_email}")
            print(f"✅ Zoom invitation sent to {candidate_email} with link: {meeting_link}")
            for attempt in range(3):  
                try:
                    with   smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:  
                        
                        server.login('rai.faisalpasha2003@gmail.com', 'bwvvnsoayfpqhnrr')  
                        server.send_message(msg)
                    print(f"✅ Email sent to {candidate_email}")
                    return 
                except Exception as e:
                    print(f"❌ Error sending email (attempt {attempt + 1}): {e}")
                    if attempt == 2:  
                        raise

            return body 
        else:
            print("❌ Failed to create Zoom meeting.")
            return None

    def send_email(self, recipient_email, subject, body):
        
        if not recipient_email:
            print("❌ Recipient email is missing.")
            return
        
        print(f"📧 Sending email to: {recipient_email}")
        print(f"📨 Subject: {subject}")
        print(f"📄 Body: {body}")


class ZoomInviteTool:
    def __init__(self, zoom_tools):
        self.zoom_tools = zoom_tools
        self.name = "zoom_invite"
        self.description = "Send a Zoom meeting invite to candidates."  

    def send_zoom_invitation(self, candidate_email):
        """
        Sends a Zoom invitation email to the candidate.
        """
        meeting_link = self.zoom_tools.send_zoom_invite(candidate_email)
        if meeting_link:
            print(f"✅ Email sent to {candidate_email} with Zoom link.")
        else:
            print(f"❌ Failed to send Zoom invitation to {candidate_email}.")


zoom_client_id = os.getenv("ZOOM_CLIENT_ID")
zoom_client_secret = os.getenv("ZOOM_CLIENT_SECRET")
zoom_account_id = os.getenv("ZOOM_ACCOUNT_ID")

def get_access_token():
    url = "https://zoom.us/oauth/token"
    credentials = f"{zoom_client_id}:{zoom_client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "account_credentials",
        "account_id": zoom_account_id
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"❌ Error obtaining access token: {response.text}")
        return None

def get_user_id(access_token):
    url = "https://api.zoom.us/v2/users/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("id")  
    else:
        print(f"❌ Error retrieving user ID: {response.text}")
        return None

# Get access token and then user ID
# access_token = get_access_token()
# if access_token:
#     user_id = get_user_id(access_token)
#     print(f"Your Zoom User ID is: {user_id}")

