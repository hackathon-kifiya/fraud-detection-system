from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Prediction Engine", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "prediction-engine"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Prediction Engine API", "version": "1.0.0"}

@app.post("/predict")
async def predict(data: dict):
    """Prediction endpoint - placeholder implementation"""
    logger.info(f"Received prediction request: {data}")
    
    # Placeholder prediction logic
    prediction = {
        "prediction": "fraud_probability",
        "confidence": 0.85,
        "model_version": "1.0.0",
        "features_used": list(data.keys()) if isinstance(data, dict) else []
    }
    
    return prediction

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5002))
    uvicorn.run(app, host="0.0.0.0", port=port)
