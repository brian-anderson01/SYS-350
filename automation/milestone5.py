from queue import Empty
import re
import time
import argparse
import getpass
from tracemalloc import stop
from unittest.loader import VALID_MODULE_NAME
from pyVmomi import vmodl, vim
from tools import service_instance, tasks, pchelper
from tools.tasks import wait_for_tasks

def creds():
    global username; global hostname; global passwd
    passwd = getpass.getpass()
    with open('user.txt') as file:
        for line in file:
            hostname, username = line.split(',') 


def sessioninfo():
    args = argparse.Namespace(host=hostname, port=443, user=username, password=passwd, disable_ssl_verification=True)
    si = service_instance.connect(args)
    session = si.content.sessionManager.currentSession

    print("--------------------------------------")
    print("Username: ",session.userName)
    print("vCenter Server: ",hostname)
    print("Source IP Address: ",session.ipAddress)
    print("--------------------------------------")



def print_vm_info(virtual_machine):

    summary = virtual_machine.summary

    if summary.config.template is not True:
        print("--------------------------------")
        print("Name:", summary.config.name)
        print("Total memory (GB): ", summary.config.memorySizeMB/1024)
        print("Number of CPU(s): ", summary.config.numCpu)
        print("Power State: ", summary.runtime.powerState)

    
        if summary.guest is not None:
            ip_address = summary.guest.ipAddress
            if ip_address:
                print("IP: ", ip_address)
            else:
                print("IP: None")
        
        if summary.runtime.question is not None:
            print("Question  : ", summary.runtime.question.text)


def getvmid():

    vmname = input("Input the name of the VM(s) you would like to select separeted by a space:  ")

    args = argparse.Namespace(host=hostname, port=443, user=username, password=passwd, disable_ssl_verification=True, find=vmname)
    si = service_instance.connect(args)
    
    content = si.RetrieveContent()

    container = content.rootFolder  # starting point to look into
    view_type = [vim.VirtualMachine]  # object types to look for
    recursive = True  # whether we should look into it recursively
    container_view = content.viewManager.CreateContainerView(
        container, view_type, recursive)
    vmname = vmname.split(" ")

    for names in vmname:
        children = container_view.view
        if names is not None:
            pat = re.compile(names, re.IGNORECASE)
            for child in children:
                if names is None:
                    print_vm_info(child)
                else:
                    if pat.search(child.summary.config.name) is not None:
                        getvmid.name = (child.summary.config.name)
                        getvmid.uuid = (child.summary.config.uuid)


def findvm():
    vmname = input("Input the name of the VM you would like to search for, or leave blank to see all  ")
    vmname = vmname.split(" ")
    args = argparse.Namespace(host=hostname, port=443, user=username, password=passwd, disable_ssl_verification=True, find=vmname)
    si = service_instance.connect(args)
    
    try:
        content = si.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        view_type = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        container_view = content.viewManager.CreateContainerView(
            container, view_type, recursive)
        for names in vmname:
            children = container_view.view
            if names is not None:
                pat = re.compile(names, re.IGNORECASE)
            for child in children:
                if names is None:
                    print_vm_info(child)
                    findvm.retr=(child.summary.config.name)
                else:
                    if pat.search(child.summary.config.name) is not None:
                        print_vm_info(child)
                        findvm.retr=(child.summary.config.name)

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0


def snapshot():
    getvmid()
    try:
        snapname = input("What would you like to name the snapshot? ")
        descript = input("Input a description for the snapshot, or leave blank ")

        args = argparse.Namespace(host=hostname, port=443, user=username, password=passwd, disable_ssl_verification=True, uuid=getvmid.uuid, name=snapname, description=descript)
        si = service_instance.connect(args)
        instance_search = False

        if not si:
            raise SystemExit("Unable to connect to host with supplied info.")

        vm = si.content.searchIndex.FindByUuid(None, args.uuid, True, instance_search)

        desc = None
        if args.description:
            desc = args.description

        task = vm.CreateSnapshot_Task(name=args.name,
                                    description=desc,
                                    memory=True,
                                    quiesce=False)
        print("Snapshot Completed.")
    
    except AttributeError as error:
        print("\nError: Please input a valid VM name")


def poweron():

    vmname = input("Input the name of the VM(s) that you would like to turn on with a space between each name: ")

    args = argparse.Namespace(host=hostname, port=443, user=username, password=passwd, disable_ssl_verification=True)
    si = service_instance.connect(args)
    vmname = vmname.split(" ")
    
    try:
        for names in vmname:
            if names is None:
                print("No virtual machines specified")

            # Retreive the list of Virtual Machines from the inventory objects
            # under the rootFolder
            content = si.content
            obj_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.VirtualMachine],
                                                            True)
            vm_list = obj_view.view
            obj_view.Destroy()

            # Find the vm and power it on
            tasks = [vm.PowerOn() for vm in vm_list if vm.name in names]

            # Wait for power on to complete
            wait_for_tasks(si, tasks)

            print(names, "has successfully been powered on")
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
    except Exception as error:
        print("Caught Exception : " + str(error))

def poweroff():

    vmname = input("Input the name of the VM(s) that you would like to turn on with a space between each name: ")

    args = argparse.Namespace(host=hostname, port=443, user=username, password=passwd, disable_ssl_verification=True)
    si = service_instance.connect(args)
    vmname = vmname.split(" ")
    
    try:
        for names in vmname:
            if names is None:
                print("No virtual machines specified")

            # Retreive the list of Virtual Machines from the inventory objects
            # under the rootFolder
            content = si.content
            obj_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.VirtualMachine],
                                                            True)
            vm_list = obj_view.view
            obj_view.Destroy()

            # Find the vm and power it on
            tasks = [vm.PowerOff() for vm in vm_list if vm.name in names]

            # Wait for power on to complete
            wait_for_tasks(si, tasks)

            print(names, "has successfully been powered off")
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
    except Exception as error:
        print("Caught Exception : " + str(error))


def deletevm():
    getvmid()

    args = argparse.Namespace(host=hostname, port=443, user=username, password=passwd, disable_ssl_verification=True, uuid=getvmid.uuid)
    si = service_instance.connect(args)

    VM = si.content.searchIndex.FindByUuid(None, args.uuid,
                                            True,
                                            False)
    
    if VM is None:
        raise SystemExit(
            "Unable to locate VirtualMachine. Arguments given: ")
    
    print ("Found: {0}".format(VM.name))
    yn = input("Are you sure you want to delete this VM? The vm will be COMPLETLY deleted! [Y]es or [N]o: ")
    yn = yn.lower()
    print(yn)
    if yn == "y":
        print ("The current powerState is: {0}".format(VM.runtime.powerState))
        if format(VM.runtime.powerState) == "poweredOn":
            print("Attempting to power off {0}".format(VM.name))
            TASK = VM.PowerOffVM_Task()
            tasks.wait_for_tasks(si, [TASK])
            print("{0}".format(TASK.info.state))

        print("Destroying VM from vSphere.")
        TASK = VM.Destroy_Task()
        tasks.wait_for_tasks(si, [TASK])
        print("Done.")


def changenet():
    """
    Simple command-line program for changing network virtual machines NIC.
    """

    netname = input("Input the name of the virtual network you would like to switch to: ")
    args = argparse.Namespace(host=hostname, port=443, user=username, password=passwd, disable_ssl_verification=True, network_name=netname)
    si = service_instance.connect(args)
    vms = input("Input the name of the VM(s) you want to edit with a space between each name: ")
    vms = vms.split(" ")

    try:
        content = si.RetrieveContent()
        vm = None

        for names in vms:
            if names:
                vm = pchelper.get_obj(content, [vim.VirtualMachine], names)

            if not names:
                raise SystemExit("Unable to locate VirtualMachine.")

            # This code is for changing only one Interface. For multiple Interface
            # Iterate through a loop of network names.
            device_change = []          
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualEthernetCard):
                    nicspec = vim.vm.device.VirtualDeviceSpec()
                    nicspec.operation = \
                        vim.vm.device.VirtualDeviceSpec.Operation.edit
                    nicspec.device = device
                    nicspec.device.wakeOnLanEnabled = True
                    nicspec.device.backing = \
                        vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
                    nicspec.device.backing.network = \
                        pchelper.get_obj(content, [vim.Network], args.network_name)
                    nicspec.device.backing.deviceName = args.network_name
                    nicspec.device.connectable = \
                        vim.vm.device.VirtualDevice.ConnectInfo()
                    nicspec.device.connectable.startConnected = True
                    nicspec.device.connectable.allowGuestControl = True
                    device_change.append(nicspec)
                    break

            config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
            task = vm.ReconfigVM_Task(config_spec)
            tasks.wait_for_tasks(si, [task])
            print("Successfully changed network for", names)

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        changenet()

    return 0


def runcmd():
    """
    Simple command-line program for executing a process in the VM without the
    network requirement to actually access it.
    """
    vmname = input("Input the name of a Linux VM you want to run a command on: ")
    vmuser = input("Input the username of a user in the VM: ")
    password = getpass.getpass()
    command = input("Input the command you would like to run: ")
    fullcommand = '-c "{}"'.format(command)
    program = "/usr/bin/bash"

    args = argparse.Namespace(host=hostname, port=443, user=username, password=passwd, disable_ssl_verification=True, vm_name=vmname, vm_user=vmuser, vm_pwd=password, path_to_program=program, program_arguments=fullcommand)
    si = service_instance.connect(args)
    try:
        content = si.RetrieveContent()
        vm = pchelper.get_obj(content, [vim.VirtualMachine], args.vm_name)

        if not vm:
            raise SystemExit("Unable to locate the virtual machine.")

        tools_status = vm.guest.toolsStatus
        if tools_status in ('toolsNotInstalled', 'toolsNotRunning'):
            raise SystemExit(
                "VMwareTools is either not running or not installed. "
                "Rerun the script after verifying that VMwareTools "
                "is running")

        creds = vim.vm.guest.NamePasswordAuthentication(
            username=args.vm_user, password=args.vm_pwd
        )

        try:
            profile_manager = content.guestOperationsManager.processManager

            if args.program_arguments:
                program_spec = vim.vm.guest.ProcessManager.ProgramSpec(
                    programPath=args.path_to_program,
                    arguments=args.program_arguments)
            else:
                program_spec = vim.vm.guest.ProcessManager.ProgramSpec(
                    programPath=args.path_to_program)

            res = profile_manager.StartProgramInGuest(vm, creds, program_spec)

            if res > 0:
                print("Program submitted, PID is %d" % res)
                pid_exitcode = \
                    profile_manager.ListProcessesInGuest(vm, creds, [res]).pop().exitCode
                # If its not a numeric result code, it says None on submit
                while re.match('[^0-9]+', str(pid_exitcode)):
                    print("Program running, PID is %d" % res)
                    time.sleep(5)
                    pid_exitcode = \
                        profile_manager.ListProcessesInGuest(vm, creds, [res]).pop().exitCode
                    if pid_exitcode == 0:
                        print("Program %d completed with success" % res)
                        break
                    # Look for non-zero code to fail
                    elif re.match('[1-9]+', str(pid_exitcode)):
                        print("ERROR: Program %d completed with Failure" % res)
                        print("  tip: Try running this on guest %r to debug"
                              % vm.summary.guest.ipAddress)
                        print("ERROR: More info on process")
                        print(profile_manager.ListProcessesInGuest(vm, creds, [res]))
                        break

        except IOError as ex:
            print(ex)
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

















def mainmenu():

    print ("""
    Select from the options below:
    1. Get session info
    2. Search for VMs and get info about them
    3. VM Options
    4. Exit
    """)


def mainoptions():
    
    mainmenu()
    option = input("Input what you would like to do: ")
    
    while option !=4:
        if option == "1":
            sessioninfo()
        elif option == "2":
            findvm()
        elif option == "3":
            vmmenu_options()
        elif option == "4":
            exit()
        else:
            print("\n Not a valid choice try again")
        mainmenu()
        option = input("Input what you would like to do: ")


def vmmenu():
    print ("""
    Select from the options below:
    1. Take a snapshot
    2. Shutdown VM(s)
    3. Power-On VM(s)
    4. Completly delete VM
    5. Change VM(s) Virtual network
    6. Run a command on a Linux VM
    7. Return to main menu
    """)

def vmmenu_options():
    vmmenu()
    option = input("Input what you would like to do: ")
    while option !=4:
        if option == "1":
            snapshot()
        elif option == "2":
            poweroff()
        elif option == "3":
            poweron()
        elif option == "4":
            deletevm()
        elif option == "5":
            changenet()
        elif option == "6":
            runcmd()
        elif option == "7":
            return()
            mainmenu()
        else:
            print("\nNot a valid choice try again")
        vmmenu()
        option = input("Input what you would like to do: ")


creds()
mainoptions()

'''
Most of the code seen here was sourced from sample scripts found on github
Some of the session info funtions was sourced from here: https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/sessions_list.py
Most of the print vm function and find vm funciton were sorced from here: https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/getallvms.py
Much of the snapshot function was taken from the following link, then edited by myself to fit my needs. https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/create_snapshot.py
Most of the power off and on function is from here: https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/vm_power_on.py
Destroy VM function code found here: https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/destroy_vm.py
Most of the network change function was found here: https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/change_vm_vif.py
The code here was essentially taken out and watered down, then added to if needed.
'''