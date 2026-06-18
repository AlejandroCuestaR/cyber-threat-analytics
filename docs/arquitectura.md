# Arquitectura

## Visión general

Cyber Threat Analytics Platform es una plataforma de análisis de datos de
ciberseguridad que cubre el ciclo completo: **ingesta → limpieza → análisis →
KPIs → visualización → Machine Learning → servicio de predicción**.

```
┌──────────────┐   ┌───────────────┐   ┌───────────────┐   ┌──────────────────┐
│  Datasets    │   │   Notebooks   │   │  Power BI     │   │   API FastAPI    │
│  (CSV crudos)│──▶│ Pandas/Sklearn│──▶│  Dashboards   │   │  POST /predict   │
│  firewall    │   │ limpieza/EDA  │   │  ejecutivo /  │   │  IsolationForest │
│  network     │   │ KPIs/ML       │   │  técnico /    │   │  (model.joblib)  │
│  login       │   │               │   │  incidentes   │   │                  │
└──────────────┘   └───────┬───────┘   └───────▲───────┘   └────────▲─────────┘
                           │                   │                    │
                           │  powerbi_dataset.csv                   │
                           └───────────────────┘     model.joblib ──┘
                              (export limpio)        (entrenado en notebook 04 /
                                                       train_model.py)
```

## Componentes

| Componente | Tecnología | Rol |
|------------|-----------|-----|
| `datasets/` | CSV | Logs crudos (firewall, tráfico de red, logins) |
| `notebooks/01` | Pandas | Limpieza y normalización |
| `notebooks/02` | Pandas + Matplotlib | Análisis exploratorio (EDA) |
| `notebooks/03` | Pandas | Cálculo de KPIs |
| `notebooks/04` | Scikit-Learn | Detección de anomalías (IsolationForest) |
| `dashboards/` | Power BI | Visualización ejecutiva, técnica e incidentes |
| `api/` | FastAPI + joblib | Servicio REST de predicción en tiempo real |

## Flujo de datos

1. **Ingesta:** los CSV crudos llegan a `datasets/` (en este proyecto se generan
   sintéticamente con `generate_datasets.py`; en un caso real provienen de
   Kaggle / CIC-IDS / SIEM).
2. **Limpieza** (`notebooks/01`): se eliminan duplicados, se imputan nulos y se
   convierten tipos. Salida: `datasets/firewall_clean.csv`.
3. **EDA y KPIs** (`notebooks/02–03`): se responden preguntas de seguridad y
   negocio y se calculan indicadores. Se exporta `dashboards/powerbi_dataset.csv`
   (vía `build_analysis.py`) para alimentar Power BI.
4. **Machine Learning** (`notebooks/04` / `train_model.py`): se entrena un
   IsolationForest sobre features agregadas por (IP, puerto) y se serializa a
   `api/model.joblib`.
5. **Servicio** (`api/`): FastAPI carga el modelo y expone `POST /predict` para
   evaluar nuevas IPs en tiempo real.

## Decisiones de diseño

- **IsolationForest** para anomalías: no requiere datos etiquetados (no
  supervisado), es eficiente y está pensado justo para detectar outliers
  (comportamientos raros) — ideal cuando no se sabe de antemano qué es un
  ataque.
- **Misma función de features en entrenamiento y servicio**
  (`api/predict.construir_features`): evita el *training/serving skew* (que el
  modelo reciba features calculadas distinto en producción).
- **Separación notebook ↔ script:** los notebooks son para exploración; la
  lógica reproducible se encapsula en `train_model.py` / `build_analysis.py`
  para CI y para alimentar la API y Power BI.
- **Power BI sobre un CSV plano enriquecido:** se exporta una tabla ya limpia y
  con columnas derivadas (hora, fecha, mes) para que el modelado en Power BI sea
  trivial.

## Reproducibilidad

```bash
python generate_datasets.py   # 1. genera/actualiza los CSV
python build_analysis.py      # 2. limpieza + KPIs + export Power BI
python train_model.py         # 3. entrena y guarda api/model.joblib
uvicorn api.main:app --reload # 4. levanta la API de predicción
```
