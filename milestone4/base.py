from dataclasses import dataclass
from pyVim.connect import SmartConnect
from pyVmomi import vmodl, vim
import ssl
import getpass

def creds():
    global username; global hostname; global passwd
    passwd = getpass.getpass()
    with open('user.txt') as file:
        for line in file:
            hostname, username = line.split(',') 

creds()

s = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
s.verify_mode = ssl.CERT_NONE
si = SmartConnect(host=hostname, user=username, pwd=passwd, sslContext=s)

aboutInfo = si.content.about
print (aboutInfo)