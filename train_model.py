"""
Entrena el modelo de detección de anomalías (IsolationForest) y lo guarda en
api/model.joblib.

Pipeline:
  1. Carga datasets/firewall_logs.csv
  2. Limpia (duplicados, nulos)
  3. Agrega eventos por (IP origen, puerto destino)
  4. Construye features con la MISMA función que usa la API (api/predict.py)
  5. Escala + entrena IsolationForest
  6. Guarda {modelo, scaler, features} con joblib

Uso:
    python train_model.py
"""
import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(__file__))
from api.predict import construir_features, FEATURES, MODEL_PATH

DATA = os.path.join(os.path.dirname(__file__), "datasets", "firewall_logs.csv")
CONTAMINATION = 0.08  # ~8% de la actividad se considera potencialmente anómala


def main():
    df = pd.read_csv(DATA)

    # --- Limpieza mínima (igual que en el notebook 01) ---
    antes = len(df)
    df = df.drop_duplicates()
    df["bytes"] = pd.to_numeric(df["bytes"], errors="coerce").fillna(0)
    df["dst_port"] = pd.to_numeric(df["dst_port"], errors="coerce").fillna(0).astype(int)
    print(f"Filas: {antes} -> {len(df)} tras quitar duplicados")

    # --- Agregación por (IP, puerto): nº de eventos ---
    agg = (
        df.groupby(["src_ip", "dst_port"])
        .size()
        .reset_index(name="eventos")
    )
    print(f"Combinaciones (IP, puerto) para entrenar: {len(agg)}")

    # --- Features (misma función que la API) ---
    X = np.array([construir_features(r.eventos, r.dst_port) for r in agg.itertuples()])

    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)

    modelo = IsolationForest(
        n_estimators=200,
        contamination=CONTAMINATION,
        random_state=42,
    )
    modelo.fit(Xs)

    # --- Reporte de anomalías detectadas en el set de entrenamiento ---
    agg["anomalia"] = modelo.predict(Xs)
    n_anom = int((agg["anomalia"] == -1).sum())
    print(f"Anomalías detectadas: {n_anom} / {len(agg)} "
          f"({100*n_anom/len(agg):.1f}%)")
    top = (agg[agg["anomalia"] == -1]
           .sort_values("eventos", ascending=False)
           .head(5))
    print("\nTop combinaciones anómalas (IP, puerto, eventos):")
    for r in top.itertuples():
        print(f"  {r.src_ip:<18} puerto {r.dst_port:<6} -> {r.eventos} eventos")

    # --- Guardar ---
    joblib.dump({"modelo": modelo, "scaler": scaler, "features": FEATURES}, MODEL_PATH)
    print(f"\nModelo guardado en {MODEL_PATH}")


if __name__ == "__main__":
    main()
