::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdCyDJGyX8VAjFD9RQg2RAE+/Fb4I5/jH97vV8RxPGus8d+8=
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSDk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJHqo23cUFClhYkqHJG7a
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off

set directories=%~dp0Directories

if not exist "%directories%" (
  mkdir "%directories%"
)

if not exist "%directories%\deletions.bat" (
  echo.> "%directories%\deletions.bat"
)

if not exist "%directories%\locations.bat" (
  echo.> "%directories%\locations.bat"
)

msg * "Select the original folder location..."
python -c "import tkinter as tk; from tkinter import filedialog; root=tk.Tk(); root.withdraw(); original_folder=filedialog.askdirectory(); print(original_folder)" > "%directories%\temp_file.txt"
set /p original_folder=<%directories%\temp_file.txt

if not exist "%original_folder%" (
  msg * "The folder %original_folder% does not exist."
  del "%directories%\temp_file.txt"
  exit /b 1
)

set new_folder=%~dp0SAVES\%~nxooriginal_folder%

if exist "%original_folder%" (
  echo RD /S /Q "%original_folder%" >> "%directories%\deletions.bat"

  if exist "%new_folder%" (
    RD /S /Q "%original_folder%"
    msg * "Original folder already exists and has been deleted."
  ) else (
    mkdir "%~dp0SAVES" 2> nul
    move /y "%original_folder%" "%new_folder%"
    echo mklink /J "%original_folder%" "%new_folder%" >> "%directories%\locations.bat"
    msg * "Original folder has been moved to the new location."
  )
)

call "%directories%\locations.bat"
call "%directories%\deletions.bat"
call "%directories%\locations.bat"

del "%directories%\temp_file.txt"
