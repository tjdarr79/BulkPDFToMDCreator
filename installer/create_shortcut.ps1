# Creates a Desktop shortcut for Bulk PDF to MD Creator, pointing at the
# app's venv (silent launcher, no console window) with the custom icon.
$ErrorActionPreference = "Stop"

$appDir = Split-Path -Parent $PSScriptRoot
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Bulk PDF to MD Creator.lnk"

$pythonw = Join-Path $appDir "venv\Scripts\pythonw.exe"
if (-not (Test-Path $pythonw)) {
    throw "Could not find $pythonw. Run install.bat first."
}

$icon = Join-Path $appDir "assets\icon.ico"
$appScript = Join-Path $appDir "app.py"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = '"' + $appScript + '"'
$shortcut.WorkingDirectory = $appDir
$shortcut.IconLocation = $icon
$shortcut.Description = "Bulk PDF to MD Creator"
$shortcut.Save()

Write-Host "Desktop shortcut created: $shortcutPath"
