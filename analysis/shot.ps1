param([string]$out, [string]$activate = '')
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
if ($activate) { $null = (New-Object -ComObject WScript.Shell).AppActivate($activate); Start-Sleep -Seconds 2 }
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
$bmp.Save($out)
