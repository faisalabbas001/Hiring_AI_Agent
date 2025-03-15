import os
import time  
from crewai import Crew
from textwrap import dedent
from dotenv import load_dotenv
from .agents import HiringAgent

load_dotenv()

def main():
    print("## Hiring Crew Agent")
    print('-------------------------------')
    
    user_email = os.getenv("USER_EMAIL") 
    if not user_email:
        print("⚠️ USER_EMAIL environment variable is not set.")
        return  


    hiring_agent = HiringAgent(user_email)

    while True:
        print("Checking for new emails...")
        
       
        hiring_agent.run()

     
        time.sleep(5)

if __name__ == "__main__":
    main()
