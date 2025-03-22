from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from crewai import Crew
from .agents import HiringAgent

load_dotenv()

app = FastAPI()

# Define a request model for user input
class UserRequest(BaseModel):
    user_email: str

@app.post("/run-agent/")
async def run_hiring_agent(request: UserRequest):
    """Runs the hiring agent process for a given user email."""
    
    if not request.user_email:
        raise HTTPException(status_code=400, detail="User email is required.")

    hiring_agent = HiringAgent(request.user_email)
    
    try:
        hiring_agent.run()
        return {"message": "Hiring process started successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

