"""
Lógica de predicción de anomalías. Centraliza:
  - la ingeniería de características (debe ser IDÉNTICA en entrenamiento y API)
  - la carga del modelo IsolationForest entrenado (api/model.joblib)
  - la traducción de la salida del modelo a un nivel de riesgo legible
"""
import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")

# Puertos típicamente abusados (acceso remoto / servicios expuestos)
PUERTOS_RIESGO = {22, 23, 445, 1433, 3306, 3389, 21}

_bundle = None


def _cargar():
    """Carga perezosa del modelo (se carga una sola vez)."""
    global _bundle
    if _bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "No existe api/model.joblib. Entrena el modelo con "
                "`python train_model.py` antes de iniciar la API."
            )
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def construir_features(eventos: int, puerto: int):
    """
    Convierte (eventos, puerto) en el vector de características que espera el
    modelo. Esta función es la fuente de verdad: train_model.py la reutiliza.
    """
    es_riesgo = 1 if int(puerto) in PUERTOS_RIESGO else 0
    return [float(eventos), float(puerto), float(es_riesgo)]


FEATURES = ["eventos", "puerto", "es_puerto_riesgo"]


def predecir(ip: str, eventos: int, puerto: int) -> dict:
    """Devuelve el nivel de riesgo y si la actividad es anómala."""
    bundle = _cargar()
    modelo = bundle["modelo"]
    scaler = bundle["scaler"]

    features = construir_features(eventos, puerto)
    X = scaler.transform([features])

    pred = modelo.predict(X)[0]          # -1 = anomalía, 1 = normal
    score = float(modelo.decision_function(X)[0])  # menor = más anómalo
    anomalia = pred == -1
    es_riesgo = features[2] == 1.0

    if anomalia and es_riesgo and eventos >= 200:
        riesgo = "critico"
    elif anomalia:
        riesgo = "alto"
    elif es_riesgo or eventos >= 200:
        riesgo = "medio"
    else:
        riesgo = "bajo"

    return {
        "ip": ip,
        "eventos": int(eventos),
        "puerto": int(puerto),
        "riesgo": riesgo,
        "anomalia": bool(anomalia),
        "score": round(score, 4),
    }
