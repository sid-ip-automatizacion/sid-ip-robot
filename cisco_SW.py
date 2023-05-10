from netmiko import ConnectHandler
import re
import pathlib
import os
import createFolder

def saveBackup_cisco_sw(ip_address, path_,clist):
    os.chdir(path_)
    device = ConnectHandler(device_type='cisco_ios', ip=ip_address, fast_cli=True,
                                username=clist[0], password=clist[1], global_delay_factor=3)
    print("backup will be stored at.. ", path_)
    output = device.send_command("show running-config",expect_string=r'#', read_timeout=90)
    fileCreator('CFG_.txt', output)
    device.disconnect()



def fileCreator(name, content):
    file = open(name, "a+")
    file.write(content)
    file.close()

def getHostname(file,path_):
    hostname = []
    os.chdir(path_)

    with open(file, "r") as myfile:
        for line in myfile:
            ips = re.findall(r'\bhostname\b', line)
            if len(ips) > 0:
                hostname.append(line)
    print(hostname[0].replace("\n", "").split(" ")[1])
    os.rename(file,'CFG_'+hostname[0].replace("\n", "").split(" ")[1]+'.txt')
    return hostname[0].replace("\n", "").split(" ")[1]


def DeviceScrapping(ip_address, cust,a_path,clist):
    print(clist)
    path_ = createFolder.create_Folder(cust, a_path)
    os.chdir(path_)
    #print(vdoms)
    
    device = ConnectHandler(device_type='cisco_ios', ip=ip_address, fast_cli=True,
                                username=clist[0], password=clist[1], global_delay_factor=3)
    body = [

        "show version",
        "show inventory",
        "show vlan",
        "show mac address-table",
        "show inter status",
        "ping 172.18.11.236",
        "ping 10.255.250.166",
        "ping 10.255.250.164",
        "ping 10.255.250.165"
    ]

    for item in body:
        #fileCreator('ATP.txt', "running "+item + " /n")
        try:
            print('currently running : ',item)
            output = device.send_command(item, expect_string=r'#', read_timeout=90)
            #fileCreator('ATP.txt', output)
            fileCreator('ATP.txt', '********** '+item +
                        ' ********** '+'\n'+'\n'+output+'\n'+'\n'+'\n')
        except:
            print('the reply for ',item ,' took too much time... !!')
    

    saveBackup_cisco_sw(ip_address, path_,clist)
    found_hostname = getHostname('CFG_.txt',path_)
    device.disconnect()
    os.rename('ATP.txt','ATP_'+found_hostname+'.txt')
    print("close the app now!")


#saveBackup_cisco_sw('10.218.128.186',r"C:\\Users\\alvaro.molano\\OneDrive - LLA\\Documentos\\programs\\results")
#getHostname('CFG_.txt',r"C:\\Users\\alvaro.molano\\OneDrive - LLA\\Documentos\\programs\\results")
#DeviceScrapping("10.216.212.138","DIRECCION GENERAL DE CONTABILIDAD GUBERNAMENTAL (DIGECOG) - 0001235563")



