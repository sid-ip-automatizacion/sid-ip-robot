
from netmiko import ConnectHandler
import re
import os

import createFolder


def saveBackup_cisco(ip_address, path_,clist):
    os.chdir(path_)
    device = ConnectHandler(device_type='cisco_ios', ip=ip_address, fast_cli=True,
                            username=clist[0], password=clist[1], global_delay_factor=3)
    print("backup will be stored at.. ", path_)
    output = device.send_command("show running-config")
    fileCreator('CFG_.txt', output)
    device.disconnect()


def fileCreator(name, content):
    file = open(name, "a+")
    file.write(content)
    file.close()


def getVrf(ip_address, path_,clist):
    os.chdir(path_)
    my_vrfs = []
    device = ConnectHandler(device_type='cisco_ios', ip=ip_address, fast_cli=True,
                            username=clist[0], password=clist[1], global_delay_factor=2)

    output = device.send_command("show ip vrf")
    fileCreator("vrfs.txt", output)
    with open("vrfs.txt", "r") as myfile:
        for line in myfile:
            res = re.search(r'  \b\D[A-Z-]{1,15}\b ', line)
            if res is not None:
                my_vrfs.append(res.group(0).strip())
    print("found VRFs : ", my_vrfs)
    device.disconnect()
    return my_vrfs


def getIps(ip_address, path_,clist):
    os.chdir(path_)
    my_ips = []
    device = ConnectHandler(device_type='cisco_ios', ip=ip_address, fast_cli=True,
                            username=clist[0], password=clist[1], global_delay_factor=2)

    output = device.send_command("show ip arp")
    fileCreator("global_arp.txt", output)
    with open("global_arp.txt", "r") as myfile:
        for line in myfile:
            res = re.search(r'  \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', line)
            if res is not None:
                my_ips.append(res.group(0).strip())
    print("found ip list in global table : ", my_ips)
    device.disconnect()
    return my_ips


def getIps_vrf(ip_address, path_, vrf_,clist):
    os.chdir(path_)
    my_ips = []
    device = ConnectHandler(device_type='cisco_ios', ip=ip_address, fast_cli=True,
                            username=clist[0], password=clist[1])

    output = device.send_command("show ip arp vrf " + vrf_)
    fileCreator("global_arp"+"_"+vrf_+".txt", output)
    with open("global_arp"+"_"+vrf_+".txt", "r") as myfile:
        for line in myfile:
            res = re.search(r'  \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', line)
            if res is not None:
                my_ips.append(res.group(0).strip())
    print("found: ", my_ips)
    for ip in my_ips:
        command = "ping vrf "+vrf_+" "+ip
        fileCreator('ATP__.txt', '\n'+'\n'+'********** '+command +
                    ' ********** '+'\n'+'\n')
        output = device.send_command(command, expect_string=r'#')
        fileCreator("ATP__.txt", output)

        command = "show ip route vrf "+vrf_
        fileCreator('ATP__.txt', '\n'+'\n'+'********** '+command +
                    ' ********** '+'\n'+'\n')
        output = device.send_command(command, expect_string=r'#')
        fileCreator("ATP__.txt", output)
    device.disconnect()
    return my_ips


def getHostname(ip_address, path_):
    os.chdir(path_)
    hostname = ''
    with open("CFG_.txt", "r") as myfile:
        for line in myfile:
            res = re.findall(r'\bhostname \b', line)
            if len(res) > 0:
                hostname = line
    return hostname.split(" ")[1].replace("\n", "")


def getInterfaces(path_):
    os.chdir(path_)
    my_interfaces = []

    with open("interfaces.txt", "r") as myfile:
        for line in myfile:
            res = re.search(
                r'GigabitEthernet\d\/\d\/\d\s|GigabitEthernet\d\s|GigabitEthernet\d\/\d\s|FastEthernet\d\s', line)
            if res is not None:
                my_interfaces.append(res.group(0).strip())
    print("found interface list : ", my_interfaces)
    return my_interfaces


def Brain(ip_address, cust, a_path,cred):
    print("################################################ MAIN ROUTINE RUNNING.. ######################################################################")
    path_ = createFolder.create_Folder(cust, a_path)
    os.chdir(path_)

    clist = [

        "show version",
        "show environment all",
        "show ip arp",
        "show mac-address-table",
        "show interfaces trunk",
        #"show interfaces | inc error",
        "show interfaces description",
        "show ip nat translations",
        "show ip dhcp binding",
        "show standby",
        "show vrrp",
        "show bgp summary",
        "show ip bgp neighbors",
        "show ip route",
        #"show ip route vrf",
        "show processes cpu sorted 5min | exclude 0.00%",
        "show crypto ikev2 sa",
        "show crypto ipsec sa",
        "show logging",
        "ping vrf CPE-MGT 10.255.250.164 repeat 50",
        "ping vrf CPE-MGT 10.255.250.166 repeat 50",
        "ping vrf CPE-MGT 172.18.11.236 repeat 50"

    ]
    saveBackup_cisco(ip_address, path_,cred)
    vrf_list = getVrf(ip_address, path_,cred)
    device = ConnectHandler(device_type='cisco_ios', ip=ip_address, fast_cli=True,
                            username=cred[0], password=cred[1])

    output = device.send_command("show ip inter brief ")
    # print(output)
    fileCreator("interfaces.txt", output)
    ips_global_list = getIps(ip_address, path_,cred)

    for ip in ips_global_list:
        try:
            command = "ping "+ip+" repeat 15"
            print("now running..... ", command)
            fileCreator('ATP__.txt', '\n'+'\n'+'********** '+command +
                        ' ********** '+'\n'+'\n')
            output = device.send_command(
                command, expect_string=r'#', read_timeout=90)
            fileCreator("ATP__.txt", output)
            fileCreator('ATP__.txt', '\n'+'\n' +
                        '********************************'+'\n'+'\n')
        except:
            print("reply took too much time ....")

    for myvrf in vrf_list:
        response = getIps_vrf(ip_address, path_, myvrf,cred)

    #ips_global_list = getIps("10.216.62.152", r"C:\\Users\\USUARIO\\Documents\\my_repo")
    for item in clist:
        #fileCreator('ATP.txt', "running "+item + " /n")
        try:
            fileCreator('ATP__.txt', ' '+'\n'+'\n')
            output = device.send_command(
                item, expect_string=r'#', read_timeout=90)
            print("now running..... ", item)
            #fileCreator('ATP.txt', output)
            fileCreator('ATP__.txt', '********** '+item +
                        ' ********** '+'\n'+'\n'+output+'\n'+'\n'+'\n')
        except:
            print("reply took too much time ....")

    inter = getInterfaces(path_)

    if len(inter) > 0:
        for item in inter:
            try:
                #fileCreator('ATP.txt', "running "+item + " /n")
                command = "show interface "+item
                print("now running..... ", command)
                fileCreator('ATP__.txt', '\n'+'\n'+'********** '+command +
                            ' ********** '+'\n'+'\n')
                output = device.send_command(
                    command, expect_string=r'#', read_timeout=90)
                #fileCreator('ATP.txt', output)
                fileCreator("ATP__.txt", output)
                fileCreator('ATP__.txt', '\n'+'\n' +
                            '********************************'+'\n'+'\n')
            except:
                print("reply took too much time ....")

    hostname = getHostname(ip_address, path_)
    print("renaming files.....")
    os.rename("CFG_.txt", "CFG_"+hostname+".txt")
    os.rename("ATP__.txt", "ATP_"+hostname+".txt")
    device.disconnect()
    print("now checking ATP file................ ",)
    try:
        Review_ploss("ATP_"+hostname+".txt",
                     path_)
    except:
        print("cant review ploss")
    try:
        Review_errors("ATP_"+hostname+".txt",
                      path_)
    except:
        print("cant review errors")
    try:
        Get_version("ATP_"+hostname+".txt",
                    path_)
    except:
        print("cant get version")
    try:
        Get_CPU("ATP_"+hostname+".txt",
                path_)
    except:
        print("cant get CPU")
    print("CAUTION: DONT FORGET TO CHECK THE LOGS!!!!!!")
    print("NOW YOU CAN CLOSE THE APP, MAIN ROUTINE TERMINATED........")


def Review_ploss(filename, path_):
    os.chdir(path_)
    list1 = []
    list2 = []
    with open(filename, "r") as myfile:
        for line in myfile:
            res = re.search(r'Echos to \d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', line)
            loss = re.search(r'Success rate is \d{1,3} percent', line)
            if res is not None:
                list1.append(res.group(0))
            if loss is not None:
                # print(line)
                list2.append(loss.group(0))

    for i in range(len(list1)):
        if '100' not in list2[i]:
            print("+++", list1[i], "results :", list2[i],
                  "--------------------------------WARNING!!!")
        else:
            print("+++", list1[i], "results :", list2[i])
    return


def Review_errors(filename, path_):
    os.chdir(path_)
    list1 = []
    list2 = []
    with open(filename, "r") as myfile:
        for line in myfile:
            res = re.search(
                r'GigabitEthernet\d\/\d\/\d is|GigabitEthernet\d is|GigabitEthernet\d\/\d is|FastEthernet\d is', line)
            loss = re.search(r'\d{1} input errors, \d{1} CRC', line)
            if res is not None:
                list1.append(res.group(0))
            if loss is not None:
                # print(line)
                list2.append(loss.group(0))

    for i in range(len(list1)):

        print("+++", list1[i].replace("is", "got"), " :", list2[i])
    return


def Get_version(filename, path_):
    os.chdir(path_)
    list1 = []
    list2 = []
    with open(filename, "r") as myfile:
        for line in myfile:
            res = re.findall(
                r'System image file is', line)
            if len(res) > 0:
                list1.append(line)

    print('\n++++++', list1[0])
    return


def Get_CPU(filename, path_):
    os.chdir(path_)
    list1 = []
    list2 = []
    with open(filename, "r") as myfile:
        for line in myfile:
            res = re.findall(
                r'CPU utilization for five seconds', line)
            if len(res) > 0:
                list1.append(line)

    print('++++++', list1[0])
    return


'''
Brain("10.216.62.152", r"C:\\Users\\USUARIO\\Documents\\my_repo\\tests")
Review_ploss("ATP_ELECTROJAPONESA_2063013.CO.txt",
             r"C:\\Users\\USUARIO\\Documents\\my_repo\\tests")
Review_errors("ATP_ELECTROJAPONESA_2063013.CO.txt",
              r"C:\\Users\\USUARIO\\Documents\\my_repo\\tests")
Get_version("ATP_ELECTROJAPONESA_2063013.CO.txt",
            r"C:\\Users\\USUARIO\\Documents\\my_repo\\tests")
Get_CPU("ATP_ELECTROJAPONESA_2063013.CO.txt",
        r"C:\\Users\\USUARIO\\Documents\\my_repo\\tests")
'''
# getInterfaces("10.216.62.152",
#              r"C:\\Users\\USUARIO\\Documents\\my_repo\\tests")
# getHostname("10.216.62.152",
#           r"C:\\Users\\USUARIO\\Documents\\my_repo\\tests")

'''
def getInterfaces_2(path_):
    os.chdir(path_)
    my_interfaces = []
    with open("interfaces.txt", "r") as myfile:
        for line in myfile:
            res = re.search(r'GigabitEthernet\d\/\d\/\d', line)
            if res is not None:
                my_interfaces.append(res.group(0).strip())
    print("found: ", my_interfaces)
    return my_interfaces



def getInterfaces(ip_address, path_):
    os.chdir(path_)
    interfaces = []
    device = ConnectHandler(device_type='cisco_ios', ip=ip_address, fast_cli=True,
                            username='sid-ip', password='sid-cw-bus1n3ss')

    output = device.send_command("show ip inter brief ")
    print(output)
    fileCreator("interfaces.txt", output)
    with open("interfaces.txt", "r") as myfile:
        for line in myfile:
            res = re.search(r'\bFastEthernet\d|\bGigabitEthernet\d\s|\bGigabitEthernet\d[\/]\d|\bGigabitEthernet\d[\/]\d[\/]\d', line)
            if res is not None:
                interfaces.append(res.group(0).strip())
    print(interfaces)

    return interfaces
'''
