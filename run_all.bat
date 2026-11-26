@echo off
start cmd /k "python app.py"
timeout /t 2 >nul
start cmd /k "python -m streamlit run searchapp.py"