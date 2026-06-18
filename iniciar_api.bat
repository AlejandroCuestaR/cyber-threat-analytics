@echo off
cd /d "%~dp0"
echo ============================================================
echo  CYBER THREAT ANALYTICS - API de prediccion
echo ============================================================
echo.

if not exist venv (
    echo No existe el entorno virtual.
    echo Ejecuta primero  instalar.bat
    echo.
    pause
    exit /b
)
call venv\Scripts\activate.bat

if not exist api\model.joblib (
    echo No existe el modelo entrenado. Entrenando ahora...
    python train_model.py
)

echo.
echo Iniciando API en http://localhost:8000/docs ...
echo (Para detener: Ctrl + C)
echo.
uvicorn api.main:app --reload
pause
