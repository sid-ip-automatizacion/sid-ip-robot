
import os
import re
import pathlib

'''
print(pathlib.Path.home().joinpath('\Desktop'))
print(pathlib.PurePosixPath('/Desktop').joinpath('here'))
p = pathlib.Path(__file__)
print('current file path', p)

path = "C:/Users/USUARIO/Desktop"
os.chdir(path)
'''


def findPloss(file):
    list1 = []
    list2 = []
    with open(file, "r") as myfile:
        for line in myfile:
            res = re.findall(r'\b\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\b ping', line)
            loss = re.findall(r'\w% packet loss', line)
            if len(res) > 0:
                list1.append(line.replace(
                    "\n", "").replace("---", "").strip().replace('ping statistics', ''))
            if len(loss) > 0:
                list2.append(line.replace(
                    "\n", "").replace("---", "").strip().replace('%', '').replace('packets transmitted', '').replace('packets received', '').replace('packet loss', '').strip())

    for item in range(len(list1)):
        if int(list2[item][-4:].replace(',', '').replace(' ', '')) > 0:
            print('----------------WARNING !!!!! ------  please check the ploss found for ip ' +
                  list1[item]+'is :  ' + list2[item][-4:].replace(',', '').replace(' ', '')+'%')

    # print(list1)
    # print(list2)


def findErrors(file):
    list1 = []
    cadena = ''
    with open(file, "r") as myfile:
        for line in myfile:

            interfaces = re.findall(
                r'\bifconfig "\w+\b"|\bifconfig "\w+-\w+\b"|\bifconfig "\w+.\w+\b', line)
            if len(interfaces) > 0:
                #print(interfaces[0].replace("ifconfig", ''))
                list1.append(interfaces[0].replace("ifconfig", ''))
                cadena = cadena + \
                    interfaces[0].replace(
                        "ifconfig", '').replace('"', '') + ' :'

            res = re.findall(r'\berrors:\b\d+', line)
            if len(res) > 0:
                if int(res[0].replace('errors:', '')) > 0:
                    list1.append(res)
                    # print(res[0])
                    cadena = cadena + ' ' + 'got errors !!  '
                else:
                    cadena = cadena + ' 0' + '  '

    print("##############################################################")
    #print(cadena.replace('got errors !!', 'X'))
    result = re.findall(r'\b\w+ : X   X\b | \b\w+ : 0   X\b | \b\w+ : X   0\b| \b[a-zA-Z]{0,10}-[a-zA-Z]{0,8}\b : X   0| \b[a-zA-Z]{0,10}-[a-zA-Z]{0,8}\b : 0   X| \b[a-zA-Z]{0,10}-[a-zA-Z]{0,8}\b : X  X',
                        cadena.replace('got errors !!', 'X'))
    # print(result)
    for i in result:
        print('----------------WARNING !!!!! ------', re.findall(r'\b[a-zA-Z]{0,10}\b | \b[a-zA-Z]{0,10}-[a-zA-Z]{0,8}\b',
                                                                 i)[0], ' got errors')
    print("##############################################################")


def getVersion(file):
    version = []

    with open(file, "r") as myfile:
        for line in myfile:
            ips = re.findall(r'\bVersion: \b', line)
            if len(ips) > 0:
                version.append(line)
    print(">> ", "UP and running :", version[0].replace(
        "Version:", '').replace("\n", ''))


def getCPUusage(file):
    cpu = []
    cpu_alarm = False
    with open(file, "r") as myfile:
        for line in myfile:
            ips = re.findall(r'\bnice \d+', line)
            if len(ips) > 0:
                cpu.append(ips[0])
    # print(cpu)
    for i in cpu:

        if int(i.replace("nice ", '')) < 20:
            cpu_alarm = True

    if cpu_alarm:
        print(">>  check the devices CPU !!")
    else:
        print(">>  no high CPU alarm found...")


def getMemoryUsage(file):
    mem = []

    with open(file, "r") as myfile:
        for line in myfile:
            ips = re.findall(r'\bMemory: \b', line)
            if len(ips) > 0:
                mem.append(line)
    print('>> ', mem[0])
