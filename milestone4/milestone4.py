import re
import argparse
import getpass
from pyVmomi import vmodl, vim
from tools import service_instance

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


def findvm():
    vmname = input("Input the name of the VM you would like to search for, or leave blank to see all  ")

    args = argparse.Namespace(host=hostname, port=443, user=username, password=passwd, disable_ssl_verification=True, find=vmname)
    si = service_instance.connect(args)
    
    try:
        content = si.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        view_type = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        container_view = content.viewManager.CreateContainerView(
            container, view_type, recursive)

        children = container_view.view
        if args.find is not None:
            pat = re.compile(args.find, re.IGNORECASE)
        for child in children:
            if args.find is None:
                print_vm_info(child)
            else:
                if pat.search(child.summary.config.name) is not None:
                    print_vm_info(child)

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0
    

creds()
sessioninfo()
findvm()