# Modelo de datos

Tres datasets de entrada y una tabla de hechos enriquecida para Power BI.

> **Datos sintéticos:** los CSV se generan con `generate_datasets.py` de forma
> determinista (semilla fija) e incluyen suciedad intencional (duplicados,
> nulos) para que la fase de limpieza sea representativa. Para usar datos
> **reales** (Kaggle / CIC-IDS-2017), reemplaza los archivos respetando estos
> mismos nombres de columna.

## 1. `firewall_logs.csv`

Eventos del firewall perimetral. Es el dataset principal del análisis y del ML.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `timestamp` | datetime | Fecha y hora del evento |
| `src_ip` | str | IP de origen |
| `dst_ip` | str | IP de destino (interna `10.0.0.x`) |
| `src_port` | int | Puerto de origen |
| `dst_port` | int | Puerto de destino (el "atacado") |
| `protocol` | str | TCP / UDP / ICMP |
| `action` | str | `allow` / `deny` |
| `bytes` | int | Bytes transferidos |
| `country` | str | País geolocalizado de la IP origen |
| `severity` | str | `baja` / `media` / `alta` / `critica` |
| `mitre_technique` | str | Técnica MITRE ATT&CK asociada (p. ej. `T1110`) |

## 2. `network_traffic.csv`

Telemetría de flujos de red (apoyo al análisis de anomalías de volumen).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `timestamp` | datetime | Momento del flujo |
| `src_ip` / `dst_ip` | str | Origen / destino |
| `protocol` | str | TCP / UDP / ICMP |
| `packet_size` | int | Tamaño de paquete (bytes) |
| `duration` | float | Duración del flujo (s) |
| `flag` | str | Flag TCP (SYN/ACK/FIN/RST/PSH) |
| `bytes_sent` | int | Bytes enviados |
| `bytes_received` | int | Bytes recibidos |

## 3. `login_attempts.csv`

Intentos de autenticación (alimenta el KPI de intentos fallidos).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `timestamp` | datetime | Momento del intento |
| `username` | str | Usuario probado |
| `src_ip` | str | IP de origen |
| `country` | str | País de origen |
| `success` | bool | ¿Login exitoso? |
| `failure_reason` | str | Motivo del fallo (`bad_password`, `user_not_found`, …) |

## Tabla de hechos para Power BI — `dashboards/powerbi_dataset.csv`

Generada por `build_analysis.py` a partir de `firewall_logs.csv` ya limpio, con
columnas derivadas para facilitar el modelado temporal:

`timestamp, fecha, hora, dia_semana, mes, src_ip, dst_ip, dst_port, protocol,
action, bytes, country, severity, mitre_technique`

## Features del modelo de ML

El IsolationForest **no** consume las tablas crudas, sino una agregación por
**(IP origen, puerto destino)**:

| Feature | Origen | Significado |
|---------|--------|-------------|
| `eventos` | `count(*)` por (IP, puerto) | Volumen de actividad |
| `puerto` | `dst_port` | Puerto objetivo |
| `es_puerto_riesgo` | derivada | 1 si el puerto es de acceso remoto/servicio crítico (22, 23, 445, 1433, 3306, 3389, 21) |

Esta misma transformación vive en `api/predict.construir_features` y se reutiliza
en entrenamiento y en la API para garantizar consistencia.
