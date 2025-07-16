"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.encoders import jsonable_encoder

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# MongoDB connection
mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(mongodb_uri)
db = client.mergington_high
activities_collection = db.activities

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.on_event("startup")
async def startup_event():
    """Populate database with initial activities data if empty"""
    # Only populate if the collection is empty
    if await activities_collection.count_documents({}) == 0:
        initial_activities = {
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
            },
            "Programming Class": {
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
            },
            "Gym Class": {
                "description": "Physical education and sports activities",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_participants": 30,
                "participants": ["john@mergington.edu", "olivia@mergington.edu"]
            },
            "Soccer Team": {
                "description": "Join the school soccer team and compete in matches",
                "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
                "max_participants": 18,
                "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
            },
            "Basketball Club": {
                "description": "Practice basketball skills and play friendly games",
                "schedule": "Thursdays, 3:30 PM - 5:00 PM",
                "max_participants": 15,
                "participants": ["liam@mergington.edu", "ava@mergington.edu"]
            },
            "Art Workshop": {
                "description": "Explore painting, drawing, and sculpture techniques",
                "schedule": "Mondays, 4:00 PM - 5:30 PM",
                "max_participants": 16,
                "participants": ["ella@mergington.edu", "jack@mergington.edu"]
            },
            "Drama Club": {
                "description": "Act, direct, and produce school plays and performances",
                "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
                "max_participants": 20,
                "participants": ["noah@mergington.edu", "grace@mergington.edu"]
            },
            "Math Olympiad": {
                "description": "Prepare for math competitions and solve challenging problems",
                "schedule": "Fridays, 4:00 PM - 5:30 PM",
                "max_participants": 10,
                "participants": ["ben@mergington.edu", "chloe@mergington.edu"]
            },
            "Science Club": {
                "description": "Conduct experiments and explore scientific concepts",
                "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
                "max_participants": 14,
                "participants": ["ethan@mergington.edu", "zoe@mergington.edu"]
            }
        }
        
        # Insert activities with their names as _id
        for name, details in initial_activities.items():
            await activities_collection.insert_one({"_id": name, **details})

@app.get("/activities")
async def get_activities():
    """Get all activities"""
    cursor = activities_collection.find()
    activities = {}
    async for doc in cursor:
        name = doc.pop('_id')
        activities[name] = doc
    return activities

@app.post("/activities/{activity_name}/signup")
async def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Get the activity
    activity = await activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate activity has available spots
    if len(activity["participants"]) >= activity["capacity"]:
        raise HTTPException(status_code=400, detail="Activity is full")
    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    # Add student
    result = await activities_collection.update_one(
        {"_id": activity_name},
        {"$push": {"participants": email}}
    )
    
    if result.modified_count:
        return {"message": f"Signed up {email} for {activity_name}"}
    raise HTTPException(status_code=500, detail="Failed to sign up for activity")

@app.delete("/activities/{activity_name}/signup")
async def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Get the activity
    activity = await activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is registered
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not registered for this activity")

    # Remove student
    result = await activities_collection.update_one(
        {"_id": activity_name},
        {"$pull": {"participants": email}}
    )
    
    if result.modified_count:
        return {"message": f"Unregistered {email} from {activity_name}"}
    raise HTTPException(status_code=500, detail="Failed to unregister from activity")
