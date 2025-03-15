from crewai import Agent
from textwrap import dedent
import os
from dotenv import load_dotenv
from pydantic import validate_email
from .tools.email_tools import EmailTools
from .tools.zoom_tools import ZoomTools, ZoomInviteTool
from crewai import LLM
import datetime
import json  
from google.oauth2.credentials import Credentials
import base64
import re


load_dotenv()

class HiringAgent:
    def __init__(self, user_email):
        self.OpenAIGPT35 = LLM(
            model="gemini/gemini-2.0-flash-exp", temperature=0.7, api_key="AIzaSyDqQsJMgF9WA9Z5Fz-qDpLZH9xeNNV2SqM"
        )
        self.user_email = user_email
        self.zoom_tools = ZoomTools() 
        self.email_tool = EmailTools(self.zoom_tools) 

        
        self.zoom_invite_tool = ZoomInviteTool(self.zoom_tools)

        
        self.credentials = Credentials.from_authorized_user_file(
            "/home/faisal-ababs/Learn_Agent_Ai/Python_Pratice/token.json",
            scopes=["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]
        )

    def email_search_agent(self):
        return Agent(
            role="Email Search Agent",
            backstory=dedent(f"""Specialist in searching and filtering emails, with expertise in Gmail API."""),
            goal=dedent(f"""Search for job hiring emails from Gmail account based on the user's criteria."""),
            tools=[self.email_tool.email_search_tool],
            verbose=True,
            llm=self.OpenAIGPT35,
        )

    def candidate_eval_agent(self):
        return Agent(
            role="Candidate Evaluation Agent",
            backstory=dedent(f"""Expert in evaluating candidates based on job-related criteria."""),
            goal=dedent(f"""Evaluate if the candidate meets the hiring criteria based on email content."""),
            tools=[self.email_tool.candidate_eval_tool],
            verbose=True,
            llm=self.OpenAIGPT35,
        )

    def zoom_invite_agent(self, candidates):
        for candidate in candidates:
           
            meeting_time = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat() 
            meeting_link = self.zoom_tools.create_zoom_meeting("Job Interview", meeting_time)

            if meeting_link:
               
                self.send_zoom_invitation(candidate, meeting_link)

    def run(self):
    
        results = self.email_tool.service.users().messages().list(
            userId="me",
            q="is:unread subject:(job OR hiring OR interview)", 
            maxResults=10
        ).execute()
        emails_json = self.email_tool.search_emails()
        emails = json.loads(emails_json)  

      
        email_list = emails.get('emails', [])

        qualified_candidates = self.email_tool.evaluate_candidate(criteria=None, emails=email_list)

       
        self.zoom_invite_agent(qualified_candidates)

    def evaluate_candidate(self, criteria, emails):
        if not emails:
            print("⚠️ No emails available for evaluation.")
            return []

        qualified_candidates = []

        for email in emails:
            body = email.get('MessageBody', '')
            print(f"Processing email from {email.get('Sender')}: {body}")  

            if ("Front-end Developer" in body and 
                "2 years" in body and 
                "Johar town lahore" in body and 
                ("famous company" in body or "well-known company" in body)):
                qualified_candidates.append(email['Sender'])
                self.send_zoom_invitation(email['Sender'], "Your Zoom meeting link here")
            else:
                self.send_encouragement_reply(email['Sender'])

        return qualified_candidates
    def send_zoom_invitation(self, candidate_email, meeting_link):
        print(f"Sending Zoom invitation to {candidate_email}")  
        if not candidate_email:
            print("❌ No candidate email provided.")
            return  

        try:
           
            subject = "Your Zoom Meeting Invitation"
            
            
            meeting_time_formatted = meeting_link.strftime('%Y-%m-%d %I:%M %p %Z')
            body = f"Dear Candidate,\n\nYou have been selected for an interview. Here is your Zoom meeting link: {meeting_link}\n\nScheduled Date and Time: {meeting_time_formatted}\n\nBest regards,\nHR Team"
            
          
            message = {
                'raw': base64.urlsafe_b64encode(body.encode()).decode()
            }
            
         
            print(f"Message to be sent: {message}")

        
            self.email_tool.service.users().messages().send(userId='me', body=message).execute()
            print(f"✅ Zoom invitation sent to {candidate_email}")
        except Exception as e:
            print(f"❌ Error sending email to {candidate_email}: {e}")

    def send_encouragement_reply(self, candidate_email):
        print(f"Sending encouragement reply to {candidate_email}")  
        try:
           
            subject = "Keep Trying!"
            body = "Dear Candidate,\n\nThank you for your application. While we appreciate your efforts, we encourage you to keep working hard and improving your skills. There will be more opportunities in the future!\n\nBest regards,\nHR Team"
            
            
            message = {
                'raw': base64.urlsafe_b64encode(body.encode()).decode()
            }
            self.email_tool.service.users().messages().send(userId='me', body=message).execute()
            print(f"✅ Encouragement reply sent to {candidate_email}")
        except Exception as e:
            print(f"❌ Error sending encouragement reply to {candidate_email}: {e}")

# Example usage
# zoom_tools = ZoomTools()
# candidate_email = "faisalabbas7959@gmail.com"  # Replace with the actual candidate's email
# zoom_tools.send_zoom_invite(candidate_email)
