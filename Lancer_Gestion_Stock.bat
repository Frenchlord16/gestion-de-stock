@echo off
title Gestion Stock
python "%~dp0gestion_stock.py"
if errorlevel 1 (
  echo.
  echo Python n'est pas installe ou n'est pas accessible.
  echo Installe Python depuis https://www.python.org/ puis relance ce fichier.
  pause
)
