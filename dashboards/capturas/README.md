python -c "
content = '''# Cyber Threat Analytics Platform

Plataforma de analisis de datos de ciberseguridad que procesa logs de red, firewall y autenticacion para generar KPIs, detectar anomalias mediante Machine Learning y exponer predicciones via API REST.

## Objetivo
Procesar mas de 40,000 registros de logs para identificar patrones de ataque, detectar comportamientos anomalos con IsolationForest y exponer un endpoint de prediccion en tiempo real. Tecnicas MITRE ATT&CK mapeadas: T1021, T1071, T1110, T1059.

## Stack tecnologico
- Analisis de datos: Python, Pandas, NumPy
- Machine Learning: Scikit-Learn (IsolationForest)
- API REST: FastAPI
- Visualizacion: Power BI, Jupyter Notebooks
- Infraestructura: Docker

## Como ejecutarlo

### Opcion A - Docker
    git clone https://github.com/AlejandroCuestaR/cyber-threat-analytics.git
    cd cyber-threat-analytics
    docker compose up --build

### Opcion B - Local
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python generate_datasets.py
    python train_model.py
    uvicorn api.main:app --reload

## Funcionalidades
- Pipeline ETL de logs de firewall, trafico de red y autenticacion
- Analisis exploratorio completo en Jupyter Notebooks
- KPIs: eventos totales, IPs unicas, intentos fallidos, eventos criticos
- Deteccion de anomalias con IsolationForest
- API REST con endpoint POST /predict para clasificacion de IPs en tiempo real
- Dashboard en Power BI con 3 paginas

## Endpoint de prediccion

POST /predict:

    {
        src_ip: 192.168.1.100,
        eventos: 450,
        puerto: 3389
    }

Respuesta:

    {
        riesgo: alto,
        anomalia: true,
        score: -0.342
    }

## Capturas

### Swagger API
![Swagger](capturas/swagger.png)

### Health Check
![Health](capturas/health.png)

### Prediccion de riesgo v0
![Predict v0](capturas/predictv0.png)

### Prediccion de riesgo v1
![Predict v1](capturas/predictv1.png)

## Hallazgos principales
- 18,031 eventos analizados en total
- 70 anomalias detectadas (0.39% del total)
- Top atacante: 45.27.52.174 (China)
- Puerto mas atacado: 3389 (RDP)
- Pico de actividad: 02:00 a 04:00 hrs
- Tecnica mas frecuente: T1021 Remote Services

## Autor
Alejandro Cuesta Rodriguez - Ingeniero en Sistemas Computacionales
https://www.linkedin.com/in/alejandro-cuesta-rodriguez-5044723a7
https://github.com/AlejandroCuestaR
'''
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('README.md creado correctamente')
"
