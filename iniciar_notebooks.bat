@echo off
cd /d "%~dp0"
echo ============================================================
echo  CYBER THREAT ANALYTICS - Notebooks (Jupyter)
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

echo Abriendo Jupyter Notebook en el navegador...
echo (Para cerrar: vuelve a esta ventana y pulsa Ctrl + C dos veces)
echo.
jupyter notebook
pause
