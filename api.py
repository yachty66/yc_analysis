from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
#from dotenv import load_dotenv
import os

#load_dotenv()

app = FastAPI()

# # Set up CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://pantheon.so", "https://www.pantheon.so"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# url: str = os.getenv("SUPABASE_URL")
# key: str = os.getenv("SUPABASE_KEY")
# supabase: Client = create_client(url, key)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/ping')
async def hello():
    return {'res': 'pong'}

# @app.get("/api/events")
# async def get_events():
#     response = supabase.table("resident_advisor").select("*").order('created_at', desc=True).limit(1).execute()
#     if hasattr(response, 'error') and response.error:
#         return {"error": str(response.error)}
#     elif hasattr(response, 'data') and response.data:
#         return {"data": response.data[0]}
#     else:
#         return {"error": "No data found or unexpected response structure"}