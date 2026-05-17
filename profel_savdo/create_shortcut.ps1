$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("C:\Users\User\Desktop\Profil Savdo.lnk")
$Shortcut.TargetPath = "C:\Users\User\Desktop\Personal Works\POS-exe\profel_savdo\release\ProfilSavdo.exe"
$Shortcut.WorkingDirectory = "C:\Users\User\Desktop\Personal Works\POS-exe\profel_savdo\release"
$Shortcut.IconLocation = "C:\Users\User\Desktop\Personal Works\POS-exe\profel_savdo\release\ProfilSavdo.exe,0"
$Shortcut.Description = "Profil Savdo POS Tizimi"
$Shortcut.Save()
Write-Host "Desktop shortcut created successfully!"
