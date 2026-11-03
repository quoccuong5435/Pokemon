param([int]$x, [int]$y, [string]$activate = 'Warcraft III')
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class M {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(int f, int dx, int dy, int d, int e);
}
"@
if ($activate) { $null = (New-Object -ComObject WScript.Shell).AppActivate($activate); Start-Sleep -Milliseconds 700 }
[M]::SetCursorPos($x, $y) | Out-Null
Start-Sleep -Milliseconds 200
[M]::mouse_event(2, 0, 0, 0, 0); Start-Sleep -Milliseconds 80; [M]::mouse_event(4, 0, 0, 0, 0)
