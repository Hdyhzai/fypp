from typing import Union
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import logging
from fastapi.middleware.cors import CORSMiddleware
from format.messageform import InputForm
from predict import APIService
import os
from models import User
from db.Supabase import SupabaseClient
from pydantic import BaseModel
import uuid
from datetime import datetime
from fastapi.encoders import jsonable_encoder
import pytz
from zoneinfo import ZoneInfo
import bcrypt
import jwt
from EnvReader import Settings

# Running with python version 3.12.7
# Developement run command -> fastapi dev main.py

logger = logging.getLogger(__name__)
app = FastAPI()
supabase = SupabaseClient.create_supabase_client()
settings = Settings()

# CORS fix
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return JSONResponse(
        content=jsonable_encoder(
            {"Message": "Welcome to the Heart Disease Prediction API"}
        ),
        status_code=200,
    )


class LoginForm(BaseModel):
    email: str
    password: str

@app.post("/login")
async def login(item: LoginForm):

    try:
        
        user = supabase.table("users").select("*").eq("email", item.email).execute()
        
        if user.data == []:
            
            response = ResponseForm(success=False, message="User not found", data={})
            
            return JSONResponse(content=jsonable_encoder(response), status_code=400)
        
        db_user_password: str = user.data[0]["password"]
        
        input_password_bytes = item.password.encode('utf-8')
        db_user_password_bytes = db_user_password.encode('utf-8')
        
        hashed_input_password = bcrypt.hashpw(input_password_bytes, db_user_password_bytes).decode('utf-8')
        
        if hashed_input_password != db_user_password:
            response = ResponseForm(success=False, message="Invalid password", data={})
            return JSONResponse(content=jsonable_encoder(response), status_code=400)

        user_dict = {
            "uuid": user.data[0]["uuid"],
            "fullname": user.data[0]["fullname"],
            "email": user.data[0]["email"],
        }
        
        token = jwt.encode(user_dict, settings.JWT_SECRET, algorithm="HS256")
        
        data = {
            "token": token,
            "user": user_dict
        }
        
        response = ResponseForm(success=True, message="Login successful", data=data)
        return JSONResponse(content=jsonable_encoder(response), status_code=200)

    except Exception as e:
        logger.error(e)
        response = ResponseForm(success=False, message="Something went wrong :(", data={})
        return JSONResponse(content=jsonable_encoder(response), status_code=400)


class SignupForm(BaseModel):
    fullname: str
    email: str
    password: str


@app.post("/signup")
async def signup(item: SignupForm):
    try:

        # Check if email is already in use
        user_check = (
            supabase.table("users").select("*").eq("email", item.email).execute()
        )

        if user_check.data:
            response = ResponseForm(success=False, message="Email already in use", data={})
            return JSONResponse(content=jsonable_encoder(response), status_code=400)

        # Check if password is less than 8 characters
        if len(item.password) < 8:
            response = ResponseForm(success=False, message="Password must be at least 8 characters", data={})
            return JSONResponse(content=jsonable_encoder(response), status_code=400)

        # Check if fullname is empty
        if not item.fullname:
            response = ResponseForm(success=False, message="Fullname is required", data={})
            return JSONResponse(content=jsonable_encoder(response), status_code=400)

        user_uuid = str(uuid.uuid4())

        # Get current time in KL
        kl_time = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))

        # Format it as timestampz (ISO format with timezone)
        timestampz = kl_time.isoformat()
        
        # converting password to array of bytes 
        bytes = item.password.encode('utf-8') 
        
        # generating the salt 
        salt = bcrypt.gensalt()
        
        # Hashing the password 
        hashed_password = bcrypt.hashpw(bytes, salt)

        user = User(
            uuid=user_uuid,
            fullname=item.fullname,
            email=item.email,
            password=hashed_password,
            created_at=timestampz,
        )

        user_dict = user.model_dump()

        response = supabase.table("users").insert(user_dict).execute()

        print(response)

        response = ResponseForm(success=True, message="User created", data={})
        return JSONResponse(content=jsonable_encoder(response), status_code=200)
    except Exception as e:
        logger.error(e)
        response = ResponseForm(success=False, message="Something went wrong :(", data={})
        return JSONResponse(content=jsonable_encoder(response), status_code=400)


@app.post("/predict")
async def post_predict(item: InputForm):
    try:

        result = APIService.predict(item)

        print(result)

        response = ResponseForm(success=True, message="Prediction successful", data={"Risk": result})
        return JSONResponse(content=jsonable_encoder(response), status_code=200)

    except Exception as e:
        logger.error(e)
        response = ResponseForm(success=False, message="Something went wrong :(", data={})
        return JSONResponse(content=jsonable_encoder(response), status_code=400)

class ResponseForm(BaseModel):
    success: bool
    message: str
    data: dict
