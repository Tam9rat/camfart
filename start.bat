@echo off
cd /d "%~dp0"
streamlit run app\main.py --server.port=8501 --server.address=127.0.0.1
