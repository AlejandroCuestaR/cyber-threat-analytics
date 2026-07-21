"""
Exporta las combinaciones (IP, puerto) evaluadas por el modelo ya entrenado
(api/model.joblib) a un CSV listo para Power BI, para la página 3
(Incidentes / Anomalías) descrita en dashboards/README.md.

Reutiliza exactamente el mismo modelo y features que la API (api/predict.py)
y que train_model.py, para que el CSV coincida con los números ya publicados
en docs/hallazgos.md (876 combinaciones, 70 anomalías, 8%).

Uso:
    python export_anomalias_powerbi.py
"""
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from api.predict import _cargar, construir_features

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, "datasets", "firewall_logs.csv")
OUT = os.path.join(BASE, "dashboards", "anomalias_powerbi.csv")


def main():
    df = pd.read_csv(DATA)
    df = df.drop_duplicates()
    df["dst_port"] = pd.to_numeric(df["dst_port"], errors="coerce").fillna(0).astype(int)

    agg = (
        df.groupby(["src_ip", "dst_port"])
        .size()
        .reset_index(name="eventos")
    )

    bundle = _cargar()
    modelo, scaler = bundle["modelo"], bundle["scaler"]

    X = [construir_features(r.eventos, r.dst_port) for r in agg.itertuples()]
    Xs = scaler.transform(X)

    agg["anomalia"] = modelo.predict(Xs) == -1
    agg["score"] = modelo.decision_function(Xs).round(4)

    agg = agg.sort_values("score")
    agg.to_csv(OUT, index=False)

    n_anom = int(agg["anomalia"].sum())
    print(f"Combinaciones: {len(agg)} | Anomalías: {n_anom} ({100*n_anom/len(agg):.1f}%)")
    print(f"Exportado a {OUT}")


if __name__ == "__main__":
    main()
