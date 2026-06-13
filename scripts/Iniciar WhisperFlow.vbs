' Inicia o WhisperFlow Local sem janela de console (residente na bandeja).
' Dê dois cliques neste arquivo para abrir o programa.
' Ajuste os caminhos abaixo se você instalou em outro local.

Dim venvPythonw, mainScript, shell
venvPythonw = "D:\WhisperFlowLocal\.venv\Scripts\pythonw.exe"
mainScript  = "D:\CloudCode-Projects\whisperflow-local\src\main.py"

Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = "D:\CloudCode-Projects\whisperflow-local\src"
' 0 = janela oculta; False = não esperar terminar (roda em segundo plano)
shell.Run """" & venvPythonw & """ """ & mainScript & """", 0, False
