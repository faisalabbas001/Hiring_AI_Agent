from crewai import Task
from textwrap import dedent
from .agents import HiringAgent

class EmailSearchTask:
    def search_emails_task(self, agent, user_email):
        return Task(
            description=dedent(
                f"""
            **Task**: Search for job-related emails in Gmail
            **Description**: Search the user's Gmail account for new emails that contain job hiring-related content. Use specific criteria to filter the emails.
            **Parameters**: 
            - User Email: {user_email}
            **Note**: Ensure that all emails are scanned and filtered correctly.
        """
            ),
            agent=agent,
            expected_output="List of emails related to job hiring."
        )

    def evaluate_candidate_task(self, agent, criteria):
        return Task(
            description=dedent(
                f"""
            **Task**: Evaluate the candidate based on criteria
            **Description**: Check the content of the job emails to see if the candidate meets the hiring criteria. Look for specific keywords or qualifications.
            **Parameters**: 
            - Criteria: {criteria}
            **Note**: Ensure only candidates that meet the full criteria are selected.
        """
            ),
            agent=agent,
            expected_output="List of candidates who meet the criteria."
        )

    def send_zoom_invite_task(self, agent):
        return Task(
            description=dedent(
                f"""
            **Task**: Send Zoom meeting invite
            **Description**: Send a Zoom meeting invite to the selected candidates.
            **Parameters**: 
            - Candidate: (Automatically selected based on email evaluation)
            **Note**: Ensure the invite includes a Zoom meeting date and time.
        """
            ),
            agent=agent,
            expected_output="Zoom meeting invitation sent."
        )

def execute_hiring_tasks(user_email):
    """
    Execute the hiring tasks for the given user email.
    """
    
    hiring_agent = HiringAgent(user_email)

  
    hiring_agent.run()

if __name__ == "__main__":
    user_email = input("Enter your Gmail address: ")
    execute_hiring_tasks(user_email)
