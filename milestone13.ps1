function deliver1 {    
    $regex = [regex] "\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    $VMS = Get-VM
    $outputArray = @()
    foreach($VM in $VMS) {
        $VMname = $VM.Name
        $VMstate = $VM.State
        $ip = $VM | Select-Object -ExpandProperty Networkadapters | Select-Object IPaddresses | Out-String
        $VMip = $regex.Matches($ip).value -join ', '

        $output = new-object psobject
        $output | add-member noteproperty "VM Name" $VMname
        $output | add-member noteproperty "PowerState" $VMstate
        $output | add-member noteproperty "IP Address" $VMip
        $outputArray += $output
    }
write-output $outputarray | sort "VM Name" | format-table * -autosize
pause
}


function deliver2 {
    $selection = Read-Host "Please input the name of the VM you would like to query"
    $outputArray = @()
    $selectionarray = $selection.split(",")
    foreach ($inputvm in $selectionarray) {
        $VM = Get-VM -Name $inputvm
        $Vhdinfo = Get-VHD -VMId $VM.VMiD

        $VMname = $VM.Name
        $VMcpu = $VM.processorCount
        $VMram = [math]::round($VM.Memoryassigned/1GB)
        $VMrep = $VM.ReplicationState
        $VHDsize = [math]::round($Vhdinfo.FileSize/1GB)
        $VMuptime = $VM.Uptime

        $output = new-object psobject
        $output | add-member noteproperty "Name" $VMname
        $output | add-member noteproperty "vCPU(s)" $VMcpu
        $output | add-member noteproperty "RAM(GB)" $VMram
        $output | add-member noteproperty "VHD Size(GB)" $VHDsize
        $output | add-member noteproperty "Replication State" $VMrep
        $output | add-member noteproperty "Uptime" $VMuptime
        $outputArray += $output
    }
write-output $outputarray | sort "VM Name" | format-table * -autosize | out-string
pause
}


function bootvm {
    $vms = Read-Host "List the VM(s) you would like to boot up"
    $vmsarray = $vms.split(",")
    foreach ($vm in $vmsarray) {
        Start-VM -Name $vm
        Write-Host "Started $vm"
    }
pause
}


function shutdownvm {
    $vms = Read-Host "List the VM(s) you would like to shutdown"
    $vmsarray = $vms.split(",")
    foreach ($vm in $vmsarray) {
        Stop-VM -Name $vm
        Write-Host "Shutdown $vm"
    }
pause
}


function snapshotvm {
    $vmname = Read-Host "Input the name of the VM you would like to take a snapshot of"
    $snapname = Read-Host "Please input a name for your snapshot"
    Get-VM -Name $vmname | Checkpoint-VM -SnapshotName $snapname
    Write-Host "Snapshot for $vmname has been created"
    pause
}


function changenetwork {
    $vmname = Read-Host "Input the name of the VM you want to edit"
    $network = Read-Host "Input the name of the virtual network you want to switch to"
    Get-VM -Name $vmname | Get-VMNetworkAdapter | Connect-VMNetworkAdapter -SwitchName $network
    Write-Host "Switched $vmname to $network"
    pause
}


function linkedclone {
    $parentvm = Read-Host "Input the name of the parent VM"
    $childhvd = Read-Host "Input the full path and name of the child vhdx"
    $linkedname = Read-Host "Input a name for the new VM"
    #$linkedram = Read-Host "Input the ram amont for the new VM in GB"

    $parentvhd = Get-VM -VMName $parentvm | Select-Object -Property VMId | Get-VHD | Select "Path" -ExpandProperty "Path" | Out-String

    New-VHD -ParentPath $parentvhd -Path $childhvd -Differencing
    New-VM -Name $linkedname -MemoryStartupBytes 2GB -VHDPath $childhvd
    Write-Host "$linkedname was created sucessfully"
    pause
}


function deletevm {
    $vmname = Read-Host "Input the name of the VM you would like to delete"
    Stop-VM -Name $vmname -Force
    Remove-VM $vmname
    Write-Host "$vmname has been removed"
    pause
}


function vm-menu {
do {
    Write-Host "1. Boot VM(s)"
    Write-Host "2. Shutdown VM(s)"
    Write-Host "3. Create a checkpoint of a VM"
    Write-Host "4. Change VM Network"
    Write-Host "5. Create Linked Clone of a VM"
    Write-Host "6. Remove a VM"
    Write-Host "7. Return to main menu"
    Write-Host "" #Blank line
    Write-Host "Note: To perform actions on multiple VMs input the VM names separated by commas without a space!"
    
    $userinputvm = Read-Host "Input what you would like to do"
    switch ($userinputvm) {
        '1' {bootvm}
        '2' {shutdownvm}
        '3' {snapshotvm}
        '4' {changenetwork}
        '5' {linkedclone}
        '6' {deletevm}
    }
}
until ($userinputvm -eq '7')
}


function mainmenu {
do {
    Write-Host "1. List all VMs with basic information about them"
    Write-Host "2. List in-depth informatin about one or more VM"
    Write-Host "3. Preform actions on a VM"
    Write-Host "4. Exit"
    Write-Host "" #Blank line
    Write-Host "Note: To perform actions on multiple VMs input the VM names separated by commas without a space!"
    
    $userinput = Read-Host "Input what you would like to do"
    switch ($userinput) {
        '1' {deliver1}
        '2' {deliver2}
        '3' {vm-menu}
    }
}
until ($userinput -eq '4')
}

mainmenu