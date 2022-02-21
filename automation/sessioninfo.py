import argparse
import getpass
from tools import service_instance

def creds():
    global username; global hostname; global passwd
    passwd = getpass.getpass()
    with open('user.txt') as file:
        for line in file:
            hostname, username = line.split(',') 

creds()

args = argparse.Namespace(host=hostname, port=443, user=username, password=passwd, disable_ssl_verification=True)
si = service_instance.connect(args)
session = si.content.sessionManager.currentSession

print("Username: ",session.userName)
print("vCenter Server: ",hostname)
print("Source IP Address: ",session.ipAddress)