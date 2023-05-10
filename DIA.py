
from distutils.errors import CompileError
from os import add_dll_directory

from netmiko import ConnectHandler
import re

import os
import time
import createFolder
import checker
import winsound


start = time.time()
#path = "C:/Users/USUARIO/Documents/my_repo"
# os.chdir(path)

# \b\w{3,4}$\b(?<!edit|Name|vdom)
# \b: \w{3,4}\b

'''
def getVdoms(ip_address, path_):
    os.chdir(path_)
    my_vdoms = []
    device = ConnectHandler(device_type='fortinet', ip=ip_address, fast_cli=True,
                            username='sid-ip', password='sid-cw-bus1n3ss', global_delay_factor=2)
    commands = ["config global", "get system vdom-property"]
    output = device.send_config_set(commands)
    #print(output)
    fileCreator("vdoms.txt", output)
    with open("vdoms.txt", "r") as myfile:
        for line in myfile:
            res = re.findall(r'\b: \w{3,4}\b', line)
            if len(res) > 0:
                my_vdoms.append(line.replace(
                    "\n", "").replace("name:", "").strip())
    print("getting all the found vdoms in the device...")
    device.disconnect()
    return my_vdoms


def getHostname(file):
    hostname = []

    with open(file, "r") as myfile:
        for line in myfile:
            ips = re.findall(r'\bHostname\b', line)
            if len(ips) > 0:
                hostname.append(line)
    print(hostname[0].replace("\n", "").split(" ")[1])

'''
def getHostname2(file, path_):
    hostname = []
    os.chdir(path_)

    with open(file, "r") as myfile:
        for line in myfile:
            ips = re.findall(r'\bHostname\b:', line)
            if len(ips) > 0:
                hostname.append(line)
    h = hostname[0].replace("\n", "").split(" ")[1]
    # print(h)
    return h


def getModel(file):
    model = []

    with open(file, "r") as myfile:
        for line in myfile:
            ips = re.findall(r'\bVersion\b', line)
            if len(ips) > 0:
                model.append(line)
    print(model[0].replace("\n", "").split(" ")[1])


def getInterfaces(ip_address, path_,clist):
    os.chdir(path_)
    interfaces = []
    device = ConnectHandler(device_type='fortinet', ip=ip_address, fast_cli=True,
                            username=clist[0], password=clist[1])
    command = 'config global'
    output = device.send_command(command, expect_string=r'#')
    command = 'show system interface'
    output = device.send_command(command, expect_string=r'#')
    fileCreator('interfaces.txt', output)
    with open('interfaces.txt', "r") as myfile:
        for line in myfile:
            # \bedit \W\b
            # \bedit "WAN-\b
            ips = re.findall(r'\bedit \W\b', line)
            if len(ips) > 0:
                interfaces.append(line.replace(
                    "\n", "").replace("edit", "").strip())
    device.disconnect()
    print('getting all the interfaces found....')

    return interfaces


def getSerial(file):
    serial = []

    with open(file, "r") as myfile:
        for line in myfile:
            ips = re.findall(r'\Serial-Number\b', line)
            if len(ips) > 0:
                serial.append(line)
    print(serial[0].replace("\n", "").split(" ")[1])


def saveBackup(ip_address, path_,clist):
    os.chdir(path_)
    device = ConnectHandler(device_type='fortinet', ip=ip_address, fast_cli=True,
                            username=clist[0], password=clist[1], global_delay_factor=3)

    print("backup will be stored at.. ", path_)
    output = device.send_command("show")
    fileCreator('config_file.txt', output)
    device.disconnect()


def ip_lookup(file):
    ip_array = []
    ping_ips = []

    with open(file, "r") as myfile:
        for line in myfile:
            # print(line)
            ips = re.findall(r'\b\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\b', line)
            if len(ips) > 0:
                ip_array.append(line)
    for item in ip_array:
        ping_ips.append(item.split(" ")[0])
    # print(ping_ips)
    return ping_ips


def fileCreator(name, content):
    file = open(name, "a+")
    file.write(content)
    file.close()


def DeviceScrapping(ip_address, cust, a_path,clist):
    max = 5
    path_ = createFolder.create_Folder(cust, a_path)
    interfaces = getInterfaces(ip_address, path_,clist)
    #vdoms = getVdoms(ip_address, path_)
    os.chdir(path_)
    # print(vdoms)
    device = ConnectHandler(device_type='fortinet', ip=ip_address, fast_cli=True,
                            username=clist[0], password=clist[1])

    command = 'get system arp'
    print('command send : \n', command)
    output = device.send_command(command, expect_string=r'#')
    print('command output \n: ', output)
    fileCreator('ARP_.txt', output)
    fileCreator('ATP.txt', '********** '+command +
                ' ********** '+'\n'+'\n'+output+'\n'+'\n'+'\n')
    IPT_ping = ip_lookup('ARP_.txt')
    print('available ip list for  : ', IPT_ping)

    '''
    for ip_item in IPT_ping:
        p = ' execute ping '+ip_item
        fileCreator('ATP.txt', '********** '+p+' ********** '+'\n')
        output = device.send_command(p, expect_string=r'#')
        fileCreator('ATP.txt', output+'\n'+'\n'+'\n')
        '''

    for ip_item in IPT_ping:
        if max > 0:
            try:
                p = ' execute ping '+ip_item
                fileCreator('ATP.txt', '********** '+p+' ********** '+'\n')
                output = device.send_command(
                    p, expect_string=r'#', read_timeout=90)
                fileCreator('ATP.txt', output+'\n'+'\n'+'\n')
                max = max - 1
            except:
                print("the reply took too much time... !!")

    body = [

        "execute ping-options repeat-count 50",
        "execute ping-options adaptive-ping enable",
        "execute ping 172.18.11.236",
        "execute ping 10.255.250.166",
        "execute ping 10.255.250.164",
        "get system status",
        "show system interface",
        "get system performance status",
        "get router info routing-table all",
        "execute dhcp lease-list",
        "get system performance status"

    ]

    for item in body:
        try:
            #fileCreator('ATP.txt', "running "+item + " /n")
            output = device.send_command(item, expect_string=r'#')
            #fileCreator('ATP.txt', output)
            fileCreator('ATP.txt', '********** '+item +
                        ' ********** '+'\n'+'\n'+output+'\n'+'\n'+'\n')
        except:
                print("the reply took too much time... !!")

    for i in interfaces:
        try:
            command = 'fnsysctl ifconfig '+i
            output = device.send_command(command, expect_string=r'#')
            #fileCreator('ATP.txt', output)
            fileCreator('ATP.txt', '********** '+command +
                        ' ********** '+'\n'+'\n'+output+'\n'+'\n'+'\n')
        except:
                print("the reply took too much time... !!")

    '''
        "fnsysctl ifconfig wan",
        "fnsysctl ifconfig wan1",
        "fnsysctl ifconfig wan2",
        "fnsysctl ifconfig lan",
        "fnsysctl ifconfig LAN",
        "sudo IPT get router info routing-table all",
        "sudo IPT execute dhcp lease-list"
    ]
    
    for item in body:

        fileCreator('ATP.txt', item)
        output = device.send_command_timing(item, delay_factor=6.0)
        fileCreator('ATP.txt', output)
    '''
    device.disconnect()

    end = time.time()
    total_time = end - start
    print("********************************************************************")
    print("***************** ATP FILES CREATED SUCCESSFULLY !!!! **************")
    print("elapsed time :" + str(total_time/60) + " minutes ")

    '''
    checker.findPloss("ATP.txt")
    checker.findErrors("ATP.txt")
    checker.getVersion("ATP.txt")
    checker.getCPUusage("ATP.txt")
    checker.getMemoryUsage("ATP.txt")
    saveBackup(ip_address, path_)
    '''
    try:
        checker.findPloss("ATP.txt")
    except Exception as e:
        print(e)
    try:
        checker.findErrors("ATP.txt")
    except Exception as e:
        print(e)
    try:
        checker.getVersion("ATP.txt")
    except Exception as e:
        print(e)
    try:
        checker.getCPUusage("ATP.txt")
    except Exception as e:
        print(e)
    try:
        checker.getMemoryUsage("ATP.txt")
    except Exception as e:
        print(e)
    saveBackup(ip_address, path_,clist)

    h = getHostname2('ATP.txt', path_)
    h = str(h) + '.txt'
    print(h)

    c = 'CFG_' + str(h)

    os.rename('ATP.txt', 'ATP_'+str(h))
    os.rename('config_file.txt', c)

    duration_ = 2000
    f = 440  # Hz
    winsound.Beep(f, duration_)
    print("....now you can close safely the app.....goin' to sleep...... bye bye")


# getVdoms("10.218.38.91")
# saveBackup("10.218.38.91")
# DeviceScrapping("10.218.66.11")
# getInterfaces("10.218.66.11")
# DeviceScrapping("10.218.95.16")
# getHostname("ATP.txt")
# getModel("ATP.txt")
# getSerial("ATP.txt")
