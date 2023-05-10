import os
import shutil
import xlsxwriter
import pathlib
from openpyxl import load_workbook
from datetime import date
import sys

who_ex = sys.executable
pHere = pathlib.Path(who_ex).parent


'''
here = os.getcwd()


'''



def create_Folder(folder_name, apath):
    path = str(pHere)+'/'+folder_name
    print('current path:', path)
    os.mkdir(path)
    os.chdir(path)

    os.mkdir(path+'/01 WO INFO')
    os.mkdir(path+'/03 RESOURCES')
    os.mkdir(path+'/04 SCRIPTS')
    os.mkdir(path+'/05 TOPOLOGY')
    os.mkdir(path+'/02 ATP')

    src = str(apath)+'/ATP_.xlsx'
    des = path+'/ATP_'+folder_name.upper()+'.xlsx'
    shutil.copy(src, des)

    os.chdir(path)
    workbook = load_workbook(filename='ATP_'+folder_name.upper()+'.xlsx')
    sheet = workbook.active
    lista = folder_name.split('-')
    sheet["A14"].value = lista[0]
    sheet["A18"].value = lista[1]

    today = date.today()
    d1 = today.strftime('%d/%m/%y')
    sheet["A33"].value = d1

    workbook.save(filename='ATP_'+folder_name.upper()+'.xlsx')
    workbook.close()

    src = str(apath)+'/LLD_.vsd'
    des = path+'/05 TOPOLOGY/LLD_'+folder_name.upper()+'.vsd'
    shutil.copy(src, des)

    print("folder con nombre :", folder_name.upper(), "....... creado")
    return path
