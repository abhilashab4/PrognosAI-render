from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from io import BytesIO
import numpy as np
import pandas as pd
import traceback

from backend.preprocessing import load_scaler, preprocess_test_file, create_test_sequences
from backend.model_service import load_model, predict_rul
from backend.dynamodb_service import save_prediction

app = FastAPI(
    title="RUL Prediction API",
    version="1.0"
)

def classify_alert(rul):
    if rul <= 10:
        return "CRITICAL"
    elif rul <= 30:
        return "WARNING"
    else:
        return "NORMAL"

@app.get("/")
def root():
    return {"message": "RUL Prediction API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
async def predict(
    domain: str = Form(...),
    test_file: UploadFile = File(...),
    rul_file: UploadFile = File(...)
):
    try:
        test_content = await test_file.read()
        rul_content = await rul_file.read()

        scaler = load_scaler(domain)
        df_test = preprocess_test_file(test_content, scaler)
        X_test = create_test_sequences(df_test, sequence_length=50)

        model = load_model(domain, X_test)
        predictions = predict_rul(X_test, model)

        true_rul = pd.read_csv(
            pd.io.common.BytesIO(rul_content),
            header=None
        ).values.flatten()

        true_rul = np.minimum(true_rul, 125)

        results = []

        for i, prediction in enumerate(predictions):

            rul = float(prediction)

            alert = classify_alert(rul)

            save_prediction(
                domain=domain,
                unit=i + 1,
                true_rul=float(true_rul[i]),
                predicted_rul=rul,
                alert=alert
            )

            results.append({
                "unit": i + 1,
                "true_rul": float(true_rul[i]),
                "predicted_rul": rul,
                "alert": alert
            })

        return {
            "domain": domain,
            "number_of_units": len(results),
            "predictions": results
        }
        
        
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__
            }
        )