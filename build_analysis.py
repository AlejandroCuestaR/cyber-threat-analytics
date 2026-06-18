"""
Ejecuta el análisis completo (limpieza + EDA + KPIs) sobre los datasets y:
  - imprime los KPIs y respuestas del EDA (números REALES)
  - exporta dashboards/powerbi_dataset.csv (tabla enriquecida para Power BI)

Es el equivalente "en script" de los notebooks 01–03, usado para verificar que
toda la cadena de análisis corre sin errores y para alimentar Power BI.

Uso:
    python build_analysis.py
"""
import os
import pandas as pd

BASE = os.path.dirname(__file__)
DS = os.path.join(BASE, "datasets")


def cargar_y_limpiar():
    df = pd.read_csv(os.path.join(DS, "firewall_logs.csv"))
    rep = {"filas_originales": len(df)}

    rep["duplicados"] = int(df.duplicated().sum())
    df = df.drop_duplicates()

    rep["nulos_country"] = int((df["country"].isna() | (df["country"] == "")).sum())
    df["country"] = df["country"].replace("", pd.NA).fillna("Desconocido")

    df["bytes"] = pd.to_numeric(df["bytes"], errors="coerce")
    rep["nulos_bytes"] = int(df["bytes"].isna().sum())
    df["bytes"] = df["bytes"].fillna(0).astype(int)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["fecha"] = df["timestamp"].dt.date
    df["hora"] = df["timestamp"].dt.hour
    df["dia_semana"] = df["timestamp"].dt.day_name()
    df["mes"] = df["timestamp"].dt.to_period("M").astype(str)

    rep["filas_limpias"] = len(df)
    return df, rep


def kpis(df):
    logins = pd.read_csv(os.path.join(DS, "login_attempts.csv"))
    fallidos = int((logins["success"].astype(str).str.lower() == "false").sum())
    return {
        "eventos_totales": int(len(df)),
        "ips_unicas": int(df["src_ip"].nunique()),
        "intentos_fallidos_login": fallidos,
        "eventos_criticos": int((df["severity"] == "critica").sum()),
        "eventos_denegados": int((df["action"] == "deny").sum()),
        "top_atacante": df["src_ip"].value_counts().idxmax(),
        "top_atacante_eventos": int(df["src_ip"].value_counts().max()),
    }


def eda(df):
    return {
        "top_5_ips": df["src_ip"].value_counts().head(5).to_dict(),
        "top_5_puertos": df["dst_port"].value_counts().head(5).to_dict(),
        "top_5_paises": df["country"].value_counts().head(5).to_dict(),
        "top_5_horas": df["hora"].value_counts().head(5).sort_index().to_dict(),
        "promedio_diario": round(df.groupby("fecha").size().mean(), 1),
        "top_mitre": df[df["mitre_technique"] != ""]["mitre_technique"]
        .value_counts().head(5).to_dict(),
        "por_mes": df.groupby("mes").size().to_dict(),
    }


def exportar_powerbi(df):
    cols = ["timestamp", "fecha", "hora", "dia_semana", "mes", "src_ip",
            "dst_ip", "dst_port", "protocol", "action", "bytes", "country",
            "severity", "mitre_technique"]
    out = os.path.join(BASE, "dashboards", "powerbi_dataset.csv")
    df[cols].to_csv(out, index=False)
    return out


def _fmt(d):
    return ", ".join(f"{k}={v}" for k, v in d.items())


if __name__ == "__main__":
    df, rep = cargar_y_limpiar()
    print("== LIMPIEZA ==")
    for k, v in rep.items():
        print(f"  {k}: {v}")

    print("\n== KPIs ==")
    for k, v in kpis(df).items():
        print(f"  {k}: {v}")

    print("\n== EDA ==")
    e = eda(df)
    print("  Top 5 IPs:    ", _fmt(e["top_5_ips"]))
    print("  Top 5 puertos:", _fmt(e["top_5_puertos"]))
    print("  Top 5 países: ", _fmt(e["top_5_paises"]))
    print("  Top horas:    ", _fmt(e["top_5_horas"]))
    print("  Top MITRE:    ", _fmt(e["top_mitre"]))
    print("  Promedio diario de eventos:", e["promedio_diario"])
    print("  Eventos por mes:", _fmt(e["por_mes"]))

    out = exportar_powerbi(df)
    print(f"\nExport Power BI -> {out}")
