@echo off
cd /d "%~dp0"
echo ============================================================
echo  CYBER THREAT ANALYTICS - Instalacion y pipeline completo
echo ============================================================
echo.

if not exist venv (
    echo [1/5] Creando entorno virtual...
    python -m venv venv
)
call venv\Scripts\activate.bat

echo [2/5] Instalando dependencias (puede tardar varios minutos)...
pip install -r requirements.txt

echo [3/5] Generando datasets...
python generate_datasets.py

echo [4/5] Limpieza + KPIs + export Power BI...
python build_analysis.py

echo [5/5] Entrenando modelo de anomalias...
python train_model.py

echo.
echo ============================================================
echo  LISTO. Ya puedes usar:
echo    - iniciar_api.bat        (API de prediccion)
echo    - iniciar_notebooks.bat  (analisis en Jupyter)
echo ============================================================
pause
