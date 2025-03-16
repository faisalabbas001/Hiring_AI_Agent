import re
from aiohttp import Payload
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
from dotenv import load_dotenv
import base64  
import json  
import PyPDF2 
import smtplib
from email.mime.text import MIMEText
from pydantic_core import Url
import requests
import datetime
from datetime import datetime, timedelta
import pytz  

load_dotenv()


class EmailSearchTool:
    def __init__(self, email_tools):
        self.name = "email_search"  
        self.func = email_tools.search_emails  
        self.description = "Search emails for job opportunities."

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class CandidateEvalTool:
    def __init__(self, email_tools):
        self.name = "candidate_eval"  
        self.func = email_tools.evaluate_candidate  
        self.description = "Evaluate candidates based on job-related criteria."

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class EmailTools:
    def __init__(self, zoom_tools):
        try:
            
            self.zoom_tools = zoom_tools
            
            
            SCOPES = [
                "https://www.googleapis.com/auth/gmail.send",  
                "https://www.googleapis.com/auth/gmail.readonly"  
            ]
            
            
            self.credentials = Credentials.from_authorized_user_file(
                "/home/faisal-ababs/Learn_Agent_Ai/Python_Pratice/token.json",
                scopes=SCOPES
            )
            self.service = build('gmail', 'v1', credentials=self.credentials)
            print("✅ Gmail API successfully connected.")

           
            self.email_search_tool = EmailSearchTool(self)
            self.candidate_eval_tool = CandidateEvalTool(self)

            self.processed_email_ids = set()  

        except Exception as e:
            print(f"❌ Error initializing Gmail API: {e}")
            self.service = None

    def search_emails(self):
        """
        Retrieve only unread emails and format the response with specific criteria.
        """
        if not self.service:        
            print("🚨 Gmail API not initialized. Check credentials.")
            return json.dumps({"error": "Gmail API not initialized."})

        try:
            results = self.service.users().messages().list(
                userId="me",
                q="is:unread subject:(job OR hiring OR interview)", 
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            email_list = []

            if not messages:
                print("⚠️ No unread emails found.")
                return json.dumps({
                    "criteria": {
                        "description": "Candidate         must meet all specified qualifications and demonstrate relevant experience in the job-related emails.",
                        "type": "Any"
                    },
                    "emails": []  
                }, ensure_ascii=False, indent=4)

            for message in messages[:5]: 
                email_id = message['id']
                if email_id in self.processed_email_ids:
                    continue  

                email = self.service.users().messages().get(
                    userId="me", 
                    id=message['id'],
                    format='full'
                ).execute()

                headers = {h['name']: h['value'] for h in email['payload']['headers']}
                body = ""
                parts = email['payload'].get('parts', [email['payload']])

                
                for part in parts:
                    if part['mimeType'] in ['text/plain', 'text/html']:
                        data = part['body'].get('data', '')
                        if data:
                            try:
                                decoded = base64.urlsafe_b64decode(data).decode('utf-8')
                                body = decoded 
                                break
                            except Exception as e:
                                print(f"⚠️ Error decoding body: {e}")
                    elif part['mimeType'] == 'app        lication/pdf':  
                        attachment_id = part['body'].get('attachmentId')
                        if attachment_id:
                            attachment = self.service.users().messages().attachments().get(
                                userId="me",
                                id=attachment_id,
                                messageId=message['id']
                            ).execute()
                            pdf_data = base64.urlsafe_b64decode(attachment['data'])
                            with open('temp.pdf', 'wb') as f:  
                                f.write(pdf_data)
                            try:
                                with open('temp.pdf', 'rb') as f:  
                                    reader = PyPDF2.PdfReader(f)
                                    pdf_text = ''
                                    for page in reader.pages:
                                        pdf_text += page.extract_text() or ''  
                            except Exception as e:
                                print(f"⚠️ Error reading PDF: {e}")
                                pdf_text = "Error reading PDF content."
                            body = pdf_text 
                            break 

                clean_body = re.sub(r'\s+', ' ', body.replace('\r\n', ' ')).strip()
                clean_snippet = re.sub(r'[\u200c\s]+', ' ', email.get('snippet', '')).strip()

                
                email_list.append({
                    'Sender': headers.get('From', 'Unknown'),
                    'Subject': headers.get('Subject', 'No Subject'),
                    'Date': headers.get('Date', 'Unknown Date'),
                    'Snippet': clean_snippet,
                    'MessageBody': clean_body[:500] + '...' if len(clean_body) > 500 else clean_body,
                    'EmailID': email_id  
                })

            return json.dumps({
                "criteria": {
                    "description": "Candidate must meet all specified qualifications and demonstrate relevant experience in the job-related emails.",
                    "type": "Any"
                },
                "emails": email_list
            }, ensure_ascii=False, indent=4) 

        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False, indent=4)

    def evaluate_candidate(self, criteria, emails):
        if not emails:
            print("⚠️ No emails available for evaluation.")
            return []

        qualified_candidates = []
        max_meetings_per_batch = 10 
        meeting_queue = []  
        sent_meeting_links = set()  
        
        karachi_tz = pytz.timezone('Asia/Karachi')
        
      
        current_time_utc = datetime.now(karachi_tz)  
        print("check that he karachi time ",current_time_utc)
        meeting_time = current_time_utc + timedelta(hours=1)  

        if meeting_time.hour < 8:
            meeting_time = meeting_time.replace(hour=8, minute=0)  
        elif meeting_time.hour >= 22:
            meeting_time = meeting_time.replace(hour=22, minute=0)  

        meeting_time_iso = meeting_time.isoformat() + 'Z'  

       
        keywords = {
            "developer": [
                "developer", "dev", "front-end developer", "frontend developer", 
                "frontedDeveloper", "web developer", "software developer", 
                "full stack developer", "fullstack developer", "UI developer", 
                "UX developer", "JavaScript developer", "React developer", 
                "Angular developer", "Vue.js developer"
            ],
            "experience": ["2 years", "two years", "2yr", "two yr"],
            "location": ["johar town lahore", "lahore", "johar town"],
            "company": ["famous company", "well-known company", "renowned company"]
        }

        for email in emails:
            body = email.get('MessageBody', '').lower() 
            email_id = email.get('EmailID')  

            
            if email_id in self.processed_email_ids:
                continue  

            print(f"Processing email from {email.get('Sender')}: {body}") 

            if (any(re.search(r'\b' + re.escape(keyword) + r'\b', body) for keyword in keywords["developer"]) and
                any(re.search(r'\b' + re.escape(exp) + r'\b', body) for exp in keywords["experience"]) and
                any(re.search(r'\b' + re.escape(loc) + r'\b', body) for loc in keywords["location"]) and
                any(re.search(r'\b' + re.escape(comp) + r'\b', body) for comp in keywords["company"])):
                
                qualified_candidates.append(email['Sender'])
                meeting_queue.append(email['Sender']) 

                
                if email['Sender'] not in sent_meeting_links:
                   
                    meeting_time_iso = (datetime.fromisoformat(meeting_time_iso[:-1]) + timedelta(hours=len(sent_meeting_links))).isoformat() + 'Z'
                    meeting_link = self.zoom_tools.create_zoom_meeting("Job Interview", meeting_time_iso) 
                    if meeting_link:  
                        self.send_zoom_invitation(email['Sender'], meeting_link, meeting_time_iso) 
                        sent_meeting_links.add(email['Sender'])  

            else:
               
                if not any(re.search(r'\b' + re.escape(keyword) + r'\b', body) for keyword in keywords["developer"]):
                    print("Criteria not met: 'Developer' not found.")
                if not any(re.search(r'\b' + re.escape(exp) + r'\b', body) for exp in keywords["experience"]):
                    print("Criteria not met: 'Experience' not found.")
                if not any(re.search(r'\b' + re.escape(loc) + r'\b', body) for loc in keywords["location"]):
                    print("Criteria not met: 'Location' not found.")
                if not any(re.search(r'\b' + re.escape(comp) + r'\b', body) for comp in keywords["company"]):
                    print("Criteria not met: 'Company' not found.")
                self.send_encouragement_reply(email['Sender'])

           
            self.processed_email_ids.add(email_id)

        
        for candidate in meeting_queue:
            meeting_link = self.zoom_tools.create_zoom_meeting("Job Interview", meeting_time_iso) 
            if meeting_link: 
                self.send_zoom_invitation(candidate, meeting_link, meeting_time_iso)  

        return qualified_candidates

    def send_email(self, to_email, message):
        msg = MIMEText(message)
        msg['Subject'] = 'Your Application Status'
        msg['From'] = os.getenv("Gmail_set")  
        msg['To'] = to_email

        for attempt in range(3): 
            try:
                with   smtplib.SMTP_SSL('smtp.gmail.com', 465) as server: 
                    
                    server.login(os.getenv("Gmail_set") ,os.getenv("Gmail_Password"))  
                    server.send_message(msg)
                print(f"✅ Email sent to {to_email}")
                return  
            except Exception as e:
                print(f"❌ Error sending email (attempt {attempt + 1}): {e}")
                if attempt == 2: 
                    raise

    def send_zoom_invitation(self, candidate_email, meeting_link, meeting_time):
        print(f"Sending Zoom invitation to {candidate_email}") 
        if not candidate_email:
            print("❌ No candidate email provided.")
            return  

        try:
            subject = "Your Zoom Meeting Invitation"
            
            
            formatted_meeting_time = datetime.fromisoformat(meeting_time[:-1]).strftime("%Y-%m-%d %I:%M %p %Z")
            
            
            body = f"Dear Candidate,\n\nYou have been selected for an interview. Here is your Zoom meeting link: {meeting_link}\nMeeting Time: {formatted_meeting_time}\n\nBest regards,\nHR Team"
            
           
            message = {
                'raw': base64.urlsafe_b64encode(body.encode()).decode()
            }
            
          
            print(f"Message to be sent: {message}")
            self.send_email(candidate_email, body)
           
            self.service.users().messages().send(userId='me', body=message).execute()
            print(f"✅ Zoom invitation sent to {candidate_email}")
        except Exception as e:
            print(f"❌ Error sending email to {candidate_email}: {e}")

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

    def send_encouragement_reply(self, candidate_email):
        print(f"Sending encouragement reply to {candidate_email}")  
        try:
            encouragement_message = "You have been working hard, keep it up! We encourage you to apply again in the future."
            self.send_email(candidate_email, encouragement_message) 
            print(f"✅ Encouragement reply sent to {candidate_email}: {encouragement_message}")
        except Exception as e:
            print(f"❌ Error sending encouragement reply to {candidate_email}: {e}")
