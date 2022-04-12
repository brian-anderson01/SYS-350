$parentvm = Read-Host "Input the name of the parent VM"
$childhvd = Read-Host "Input the full path and name of the child vhdx"
$linkedname = Read-Host "Input a name for the new VM"
#$linkedram = Read-Host "Input the ram amont for the new VM in GB"

$parentvhd = Get-VM -VMName $parentvm | Select-Object -Property VMId | Get-VHD | Select "Path" -ExpandProperty "Path" | Out-String

New-VHD -ParentPath $parentvhd -Path $childhvd -Differencing
New-VM -Name $linkedname -MemoryStartupBytes 2GB -VHDPath $childhvd

Write-Host "$linkedname was created sucessfully"
