@echo off
echo.
echo ============================================
echo    Gestor de Empresas - Instalacao
echo ============================================
echo.

echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo ============================================
echo    Instalacao concluida!
echo ============================================
echo.
echo Para iniciar o aplicativo, execute:
echo     streamlit run app.py
echo.
pause
