from typing import Union
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import logging
from fastapi.middleware.cors import CORSMiddleware
from format.messageform import InputForm
from predict import APIService

# Running with python version 3.12.7
# Developement run command -> fastapi dev main.py

logger = logging.getLogger(__name__)
app = FastAPI()

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
    return JSONResponse(content=jsonable_encoder({"Message": "Welcome to the Heart Disease Prediction API"}), status_code=200)

@app.post("/predict")
async def post_predict(item: InputForm):
    try:

        result = APIService.predict(item)

        print(result)

        return JSONResponse(content=jsonable_encoder({"Risk": result}), status_code=200)

    except Exception as e:
        logger.error(e)
        return JSONResponse(content=jsonable_encoder({"Message": "Something went wrong :("}), status_code=400)