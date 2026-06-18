# Hallazgos

Resultados obtenidos al ejecutar el pipeline completo sobre el dataset
(`firewall_logs.csv`, 18,360 filas crudas → **18,031** tras limpieza).

> Reproducible con `python build_analysis.py` y `python train_model.py`.

## Limpieza

| Métrica | Valor |
|---------|------:|
| Filas originales | 18,360 |
| Duplicados eliminados | 329 |
| Nulos/vacíos en `country` (→ "Desconocido") | 550 |
| Nulos en `bytes` (→ 0) | 183 |
| **Filas finales** | **18,031** |

Transformaciones: `drop_duplicates`, imputación de `country` y `bytes`,
conversión de `timestamp` a datetime y derivación de `fecha`, `hora` y `mes`.

## KPIs

| KPI | Valor |
|-----|------:|
| Eventos totales | 18,031 |
| IPs únicas (activos monitoreados) | 124 |
| Intentos fallidos de login | 5,085 |
| Eventos críticos | 5,445 |
| Eventos denegados por el firewall | 8,700 |
| **Top atacante** | **45.21.111.60** (1,281 eventos) |

## Análisis exploratorio (EDA)

### ¿Cuáles son las IP más activas?
Las 5 IPs más activas son **todas externas del rango `45.x`** (entre 1,223 y
1,281 eventos cada una), claramente separadas del resto del tráfico interno:

| IP | Eventos |
|----|--------:|
| 45.21.111.60 | 1,281 |
| 45.74.13.144 | 1,266 |
| 45.27.52.174 | 1,249 |
| 45.45.125.58 | 1,228 |
| 45.91.57.7 | 1,223 |

### ¿Qué puertos son los más atacados?
Dominan puertos de **servicios y acceso remoto**: `3306` (MySQL), `22` (SSH),
`8080`, `21` (FTP) y `3389` (RDP) — todos con ~1,235–1,247 eventos.

### ¿Qué países generan más eventos?
**China (4,127)** y **Rusia (3,795)** encabezan, seguidos de **Corea del Norte
(2,761)** e **Irán (2,521)**. El tráfico legítimo (México, EE. UU.) queda muy por
debajo.

### ¿Qué horas tienen más actividad?
La actividad se concentra en la **madrugada (00:00–04:00h)**, ~1,730–1,800
eventos por hora — patrón típico de **ataques automatizados** fuera del horario
laboral.

### Negocio
- **Promedio diario de eventos:** 300.5
- **Tendencia mensual:** Enero 2024 = 9,368 · Febrero 2024 = 8,663
- **Top técnicas MITRE:** `T1190` Exploit Public-Facing App (3,699) ·
  `T1110` Brute Force (2,468) · `T1021` Remote Services (2,467) ·
  `T1071` App Layer Protocol (1,239)

## Detección de anomalías (IsolationForest)

- Se entrenó sobre **876** combinaciones (IP, puerto).
- Se detectaron **70 anomalías (8.0%)**.
- Las anomalías corresponden a **IPs externas `45.x` atacando puertos de acceso
  remoto** (RDP 3389, SMB 445, Telnet 23, FTP 21) con **175–186 eventos** cada
  una: firma inequívoca de **fuerza bruta / escaneo dirigido**.

## Conclusiones para el equipo SOC

1. **Bloquear/limitar el rango `45.x`**: concentra el grueso de los eventos
   denegados y todas las anomalías.
2. **Exponer menos servicios**: RDP (3389), SSH (22) y SMB (445) no deberían ser
   accesibles desde Internet; mover detrás de VPN/bastión.
3. **Reforzar autenticación**: 5,085 intentos fallidos indican fuerza bruta →
   MFA + bloqueo por intentos + alertas.
4. **Vigilancia reforzada en madrugada**: la mayor parte del ataque ocurre
   00:00–04:00h; conviene alertas automáticas en esa ventana.
