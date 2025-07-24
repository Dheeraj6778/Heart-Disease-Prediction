from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import joblib
from pydantic import BaseModel, Field

app = FastAPI()
scaler = joblib.load('./model/scaler.pkl')
model = joblib.load('./model/model.pkl')

class Input(BaseModel):
    exang_True: int = Field(..., ge=0, le=1)
    cp_atypical_angina: int = Field(..., ge=0, le=1)
    thalch: float = Field(..., gt=0, le=250)
    oldpeak: float = Field(..., ge=0.0, le=10.0)
    sex_Male: int = Field(..., ge=0, le=1)
    age: int = Field(..., ge=1, le=120)
    chol: float = Field(..., gt=0, le=600)
    cp_non_anginal: float = Field(..., ge=0.0, le=1.0)
    fbs_True: int = Field(..., ge=0, le=1)
    restecg_st_t_abnormality: int = Field(..., ge=0, le=1)
    trestbps: float = Field(..., gt=0, le=300)


@app.post("/predict")
def predict(data: Input):

    input_array = np.array([
        data.exang_True,                   #0
        data.cp_atypical_angina,           #1
        data.thalch,                       # 2 (scaled)
        data.oldpeak,                     # 3 (scaled)
        data.sex_Male,                    #4
        data.age,                         # 5 (scaled)
        data.chol,                        # 6 (scaled)
        data.cp_non_anginal,              #7
        data.fbs_True,                    #8
        data.restecg_st_t_abnormality,    #9
        data.trestbps                     # 10 (scaled)
    ])


    numerical_indices = [2, 3, 5, 6, 10]
    numerical_values = input_array[numerical_indices].reshape(1, -1) # transforms into a 2d array as transform function accepts 2d only
    scaled_numerical = scaler.transform(numerical_values).flatten() # again convert back to 1d

    full_scaled_input = input_array.copy()
    for i, idx in enumerate(numerical_indices):
        full_scaled_input[idx] = scaled_numerical[i]

    prediction = model.predict(full_scaled_input.reshape(1, -1)) 

    return {
        "input_array": input_array.tolist(),
        "scaled_input": full_scaled_input.tolist(),
        "prediction": int(prediction[0])
    }


@app.get("/health",status_code=200)
def health():
    return JSONResponse(status_code=200,content={"status":"ok"})