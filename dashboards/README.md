# Dashboard de Power BI

El archivo binario `dashboard.pbix` debe construirse desde **Power BI Desktop**
(no se puede generar por código). Aquí está todo lo necesario para armarlo en
~30 minutos a partir del dataset ya preparado.

## Fuente de datos

`dashboards/powerbi_dataset.csv` (generado por `python build_analysis.py`).
Es la tabla de hechos de firewall ya **limpia y enriquecida** con columnas
`fecha`, `hora`, `dia_semana`, `mes`, `severity`, `mitre_technique`, etc.

> Para login/tráfico, puedes cargar también `datasets/login_attempts.csv` y
> `datasets/network_traffic.csv` como tablas adicionales.

## Cómo construirlo

1. Abre **Power BI Desktop** → *Obtener datos* → **Texto/CSV** →
   `powerbi_dataset.csv`.
2. (Opcional) En *Transformar datos* confirma tipos: `fecha` como Fecha,
   `bytes`/`dst_port` como número entero.
3. Crea las **3 páginas** descritas abajo.
4. Guarda como `dashboards/dashboard.pbix`.
5. Exporta capturas (PNG) de cada página a `dashboards/capturas/`.

## Página 1 — Ejecutiva

| Visual | Campo / medida |
|--------|----------------|
| Tarjeta: **Total eventos** | `Recuento de filas` |
| Tarjeta: **Eventos críticos** | `Recuento` filtrado a `severity = "critica"` |
| Gráfico de barras: **Top amenazas (MITRE)** | `mitre_technique` por recuento |
| Gráfico de líneas: **Tendencia mensual** | eje `mes`, valor recuento |

Medidas DAX útiles:

```DAX
Eventos Totales = COUNTROWS('powerbi_dataset')
Eventos Criticos = CALCULATE(COUNTROWS('powerbi_dataset'), 'powerbi_dataset'[severity] = "critica")
Eventos Denegados = CALCULATE(COUNTROWS('powerbi_dataset'), 'powerbi_dataset'[action] = "deny")
```

## Página 2 — Técnica

| Visual | Campo |
|--------|-------|
| Barras: **Top IPs** | `src_ip` por recuento (Top N = 10) |
| Mapa: **Geográfico** | `country` por recuento |
| Barras: **Puertos más usados** | `dst_port` por recuento |
| Matriz/Heatmap: **Actividad** | filas `dia_semana`, columnas `hora`, valor recuento |

## Página 3 — Incidentes

| Visual | Campo |
|--------|-------|
| Dona: **Eventos por severidad** | `severity` |
| Barras: **Distribución MITRE ATT&CK** | `mitre_technique` |
| Tabla/Dispersión: **Anomalías** | une la salida del notebook 04 (IP, puerto, eventos, anomalía) |

> Para la sección de anomalías puedes exportar desde el notebook 04 un CSV con
> las combinaciones marcadas como anómalas y cargarlo como tabla adicional.

## Capturas esperadas (`dashboards/capturas/`)

- `ejecutiva.png`
- `tecnica.png`
- `incidentes.png`
