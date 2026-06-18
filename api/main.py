"""
API de predicción de anomalías (FastAPI).

Ejecutar desde la raíz del proyecto:
    uvicorn api.main:app --reload

Endpoints:
    GET  /              -> healthcheck
    GET  /health        -> estado del modelo
    POST /predict       -> predice riesgo/anomalía para una IP
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from . import predict
except ImportError:  # permite `python api/main.py`
    import predict

app = FastAPI(
    title="Cyber Threat Analytics — API de Predicción",
    description="Detección de anomalías de red con IsolationForest.",
    version="1.0.0",
)


class PredictRequest(BaseModel):
    ip: str = Field(..., examples=["192.168.1.100"])
    eventos: int = Field(..., ge=0, examples=[450])
    puerto: int = Field(..., ge=0, le=65535, examples=[3389])


class PredictResponse(BaseModel):
    ip: str
    eventos: int
    puerto: int
    riesgo: str
    anomalia: bool
    score: float


@app.get("/")
def root():
    return {"servicio": "Cyber Threat Analytics API", "estado": "ok"}


@app.get("/health")
def health():
    try:
        predict._cargar()
        return {"modelo_cargado": True}
    except FileNotFoundError as e:
        return {"modelo_cargado": False, "detalle": str(e)}


@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(req: PredictRequest):
    return predict.predecir(req.ip, req.eventos, req.puerto)
