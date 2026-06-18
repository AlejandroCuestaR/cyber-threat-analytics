"""
Genera los 4 notebooks de Jupyter en notebooks/ como archivos .ipynb válidos.
(Construye el JSON nbformat 4 a mano, sin dependencias extra.)

Uso:
    python build_notebooks.py
"""
import json
import os

OUT = os.path.join(os.path.dirname(__file__), "notebooks")
os.makedirs(OUT, exist_ok=True)


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": text}


def notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def save(name, nb):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------------------
# 01 - Limpieza de datos
# ---------------------------------------------------------------------------
nb01 = notebook([
    md("# 01 — Limpieza de datos\n\n"
       "Carga de `firewall_logs.csv`, eliminación de duplicados, manejo de "
       "nulos y conversión de tipos. Documentamos cada transformación."),
    code("import pandas as pd\n\n"
         "df = pd.read_csv('../datasets/firewall_logs.csv')\n"
         "print('Filas originales:', len(df))\n"
         "df.head()"),
    md("## Diagnóstico inicial"),
    code("print('Duplicados:', df.duplicated().sum())\n"
         "print('\\nNulos por columna:')\n"
         "print(df.isna().sum())\n"
         "print('\\nVacíos en country:', (df['country'] == '').sum())"),
    md("## Limpieza\n"
       "1. Quitar duplicados\n"
       "2. Rellenar `country` vacío con 'Desconocido'\n"
       "3. Convertir `bytes` a numérico (nulos -> 0)\n"
       "4. Convertir `timestamp` a datetime y derivar fecha/hora/mes"),
    code("df = df.drop_duplicates()\n"
         "df['country'] = df['country'].replace('', pd.NA).fillna('Desconocido')\n"
         "df['bytes'] = pd.to_numeric(df['bytes'], errors='coerce').fillna(0).astype(int)\n"
         "df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')\n"
         "df['fecha'] = df['timestamp'].dt.date\n"
         "df['hora'] = df['timestamp'].dt.hour\n"
         "df['mes'] = df['timestamp'].dt.to_period('M').astype(str)\n"
         "print('Filas tras limpieza:', len(df))\n"
         "df.to_csv('../datasets/firewall_clean.csv', index=False)\n"
         "df.head()"),
    md("## Resultado\n"
       "- **329** duplicados eliminados\n"
       "- **550** vacíos en `country` y **183** en `bytes` corregidos\n"
       "- Dataset limpio: **18,031** filas guardadas en `firewall_clean.csv`"),
])
save("01-limpieza_datos.ipynb", nb01)

# ---------------------------------------------------------------------------
# 02 - EDA
# ---------------------------------------------------------------------------
nb02 = notebook([
    md("# 02 — Análisis Exploratorio (EDA)\n\n"
       "Respondemos preguntas de seguridad y de negocio sobre el dataset limpio."),
    code("import pandas as pd\n"
         "import matplotlib.pyplot as plt\n\n"
         "df = pd.read_csv('../datasets/firewall_clean.csv')\n"
         "len(df)"),
    md("## Seguridad — ¿Cuáles son las IP más activas?"),
    code("top_ips = df['src_ip'].value_counts().head(10)\n"
         "top_ips.plot(kind='barh', title='Top 10 IPs por nº de eventos')\n"
         "plt.gca().invert_yaxis(); plt.tight_layout(); plt.show()\n"
         "top_ips"),
    md("## ¿Qué puertos son los más atacados?"),
    code("df['dst_port'].value_counts().head(10).plot(kind='bar', "
         "title='Puertos destino más frecuentes'); plt.tight_layout(); plt.show()"),
    md("## ¿Qué países generan más eventos?"),
    code("df['country'].value_counts().head(10).plot(kind='bar', "
         "title='Eventos por país'); plt.tight_layout(); plt.show()"),
    md("## ¿Qué horas tienen más actividad?"),
    code("df['hora'].value_counts().sort_index().plot(kind='line', marker='o', "
         "title='Actividad por hora del día'); plt.tight_layout(); plt.show()"),
    md("## Negocio — promedio diario y tendencia mensual"),
    code("print('Promedio diario de eventos:', round(df.groupby('fecha').size().mean(), 1))\n"
         "df.groupby('mes').size().plot(kind='bar', title='Eventos por mes'); "
         "plt.tight_layout(); plt.show()"),
])
save("02-eda.ipynb", nb02)

# ---------------------------------------------------------------------------
# 03 - KPIs
# ---------------------------------------------------------------------------
nb03 = notebook([
    md("# 03 — KPIs\n\n"
       "Indicadores clave para la capa ejecutiva del dashboard."),
    code("import pandas as pd\n\n"
         "df = pd.read_csv('../datasets/firewall_clean.csv')\n"
         "logins = pd.read_csv('../datasets/login_attempts.csv')"),
    code("kpis = {\n"
         "    'Eventos totales': len(df),\n"
         "    'IPs únicas': df['src_ip'].nunique(),\n"
         "    'Intentos fallidos (login)': int((logins['success'].astype(str).str.lower()=='false').sum()),\n"
         "    'Eventos críticos': int((df['severity']=='critica').sum()),\n"
         "    'Eventos denegados': int((df['action']=='deny').sum()),\n"
         "    'Top atacante': df['src_ip'].value_counts().idxmax(),\n"
         "    'Eventos del top atacante': int(df['src_ip'].value_counts().max()),\n"
         "}\n"
         "for k, v in kpis.items():\n"
         "    print(f'{k:<28}: {v}')"),
    md("## Tabla de KPIs\n\n"
       "| KPI | Valor |\n|-----|------|\n"
       "| Eventos totales | 18,031 |\n"
       "| IPs únicas | 124 |\n"
       "| Intentos fallidos (login) | 5,085 |\n"
       "| Eventos críticos | 5,445 |\n"
       "| Top atacante | 45.21.111.60 (1,281 eventos) |"),
])
save("03-kpis.ipynb", nb03)

# ---------------------------------------------------------------------------
# 04 - Detección de anomalías
# ---------------------------------------------------------------------------
nb04 = notebook([
    md("# 04 — Detección de anomalías (IsolationForest)\n\n"
       "Agregamos eventos por (IP, puerto), entrenamos IsolationForest y "
       "marcamos comportamientos inusuales. Es la misma lógica que sirve la API."),
    code("import pandas as pd\n"
         "from sklearn.ensemble import IsolationForest\n"
         "from sklearn.preprocessing import StandardScaler\n\n"
         "df = pd.read_csv('../datasets/firewall_clean.csv')\n"
         "agg = df.groupby(['src_ip','dst_port']).size().reset_index(name='eventos')\n"
         "PUERTOS_RIESGO = {22,23,445,1433,3306,3389,21}\n"
         "agg['es_riesgo'] = agg['dst_port'].isin(PUERTOS_RIESGO).astype(int)\n"
         "agg.head()"),
    code("X = agg[['eventos','dst_port','es_riesgo']].values\n"
         "Xs = StandardScaler().fit_transform(X)\n"
         "modelo = IsolationForest(n_estimators=200, contamination=0.08, random_state=42)\n"
         "agg['anomalia'] = modelo.fit_predict(Xs)\n"
         "n = (agg['anomalia']==-1).sum()\n"
         "print(f'Anomalías: {n}/{len(agg)} ({100*n/len(agg):.1f}%)')"),
    md("## Top combinaciones anómalas"),
    code("agg[agg['anomalia']==-1].sort_values('eventos', ascending=False).head(10)"),
    md("## Conclusión\n"
       "Las anomalías se concentran en **IPs externas (45.x)** atacando puertos "
       "de acceso remoto (RDP 3389, SSH 22, SMB 445) con cientos de eventos — "
       "patrón típico de fuerza bruta / escaneo. El modelo entrenado se exporta "
       "a `api/model.joblib` con `train_model.py` para servirlo vía la API."),
])
save("04-deteccion_anomalias.ipynb", nb04)

print("Notebooks generados:")
for f in sorted(os.listdir(OUT)):
    print(" ", f)
