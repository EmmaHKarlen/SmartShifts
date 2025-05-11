import sys
from fastapi import FastAPI
import uvicorn

sys.path.append('c:/Users/User/Desktop/smartShifts/SmartShifts/app')

from models.shift import CreateShiftRequest
from services.shift_service import ShiftService

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the SmartShifts API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
def startup_event():
    global shift_service
    try:
        shift_service = ShiftService()
    except Exception as e:
        print("Error")

@app.post("/generate_monthly_shifts")
def generate_monthly_shifts(request: CreateShiftRequest):
    response = shift_service.create_monthly_shifts(request.month)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

