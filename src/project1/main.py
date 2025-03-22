# import os
# import time  
# from crewai import Crew
# from textwrap import dedent
# from dotenv import load_dotenv
# from .agents import HiringAgent

# load_dotenv()

# def main():
#     print("## Hiring Crew Agent")
#     print('-------------------------------')
    
#     user_email = os.getenv("USER_EMAIL") 
#     if not user_email:
#         print("⚠️ USER_EMAIL environment variable is not set.")
#         return  


#     hiring_agent = HiringAgent(user_email)

#     while True:
#         print("Checking for new emails...")
        
       
#         hiring_agent.run()

     
#         time.sleep(5)

# if __name__ == "__main__":
#     main()

import os
import time
import threading
import uvicorn
from fastapi import FastAPI
from crewai import Crew
from dotenv import load_dotenv
from .agents import HiringAgent
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

running = False


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:5173"] for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

def run_agent():
    """Function to continuously check emails using the HiringAgent."""
    global running
    user_email = os.getenv("USER_EMAIL")
    if not user_email:
        print("⚠️ USER_EMAIL environment variable is not set.")
        return

    hiring_agent = HiringAgent(user_email)

    while running:
        print("Checking for new emails...")
        hiring_agent.run()
        time.sleep(5)

@app.get("/")
def read_root():
    return {"message": "Hiring Agent API is running!"}
 
  
@app.post("/start")
def start_agent():
    """Start the hiring agent process."""
    global running
    if not running:
        running = True
        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()
        return {"status": "Agent started!"}
    return {"status": "Agent is already running!"}

@app.post("/stop")
def stop_agent():
    """Stop the hiring agent process."""
    global running
    running = False
    return {"status": "Agent stopped!"}

def main():
    """Main function to start FastAPI on a specific port."""
    print("## Hiring Crew Agent API is starting on port 8001...")
    port = int(os.environ.get("PORT"))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()










# import os  
# import time  
# from fastapi import FastAPI  
# from dotenv import load_dotenv  
# from .agents import HiringAgent  

# load_dotenv()  

# app = FastAPI()  

# @app.get("/")  
# def home():  
#     return {"message": "Hiring Agent API is running"}  

# @app.post("/run-hiring-agent")  
# def run_hiring_agent():  
#     user_email = os.getenv("USER_EMAIL")  
#     if not user_email:  
#         return {"error": "⚠️ USER_EMAIL environment variable is not set."}  

#     hiring_agent = HiringAgent(user_email)  
#     hiring_agent.run()  

#     return {"message": "Hiring Agent has started processing"}  

# def main():  
#     print("## Hiring Crew Agent")  
#     print('-------------------------------')  
#     home()  

# if __name__ == "__main__":  
#     main()  