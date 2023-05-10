import tkinter as tk
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter import messagebox
import fortinet_atp
import DIA
import re
import sys
import os
import RT_cisco

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))


def on_enter(event):
    myb.configure(relief="sunken")


def on_out(event):
    myb.configure(relief="raised")


def handle_click(event):
    print(case_cb.get())
    validate_name = False

    print("ip DCN :"+DCN_tx.get("1.0", "end-1c"))
    print("customer :"+WO_tx.get("1.0", "end-1c"))

    valid_ip = re.findall(
        r'(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}', DCN_tx.get("1.0", "end-1c"))
    print(valid_ip)

    valid_customer = re.findall(
        r'\w+-{1}\d+', WO_tx.get("1.0", "end-1c"))
    print(valid_customer)
    '''
    if len(valid_customer) != 0:
        validate_name = True
    else:
        validate_name = False
        messagebox.showinfo(
            "message", "customer name must be like 'CUSTOMER NAME-DEALCODE' format")
    '''

    if case_cb.get() == 'fortinet-vdoms':
        print('vdoms')
        fortinet_atp.DeviceScrapping(DCN_tx.get(
            "1.0", "end-1c"), WO_tx.get("1.0", "end-1c"), application_path)
    elif case_cb.get() == 'DIA':
        print('DIA')
        DIA.DeviceScrapping(DCN_tx.get(
            "1.0", "end-1c"), WO_tx.get("1.0", "end-1c"), application_path)
    elif case_cb.get() == 'cisco RT':
        print('cisco RT')
        RT_cisco.Brain(DCN_tx.get(
            "1.0", "end-1c"), WO_tx.get("1.0", "end-1c"), application_path)


root = tk.Tk(className=" ATP_GUI")
root.geometry("1300x400")
cases = ('fortinet-vdoms', 'DIA', 'cisco RT')

# go button
myb = tk.Button(text="Send", width=10, height=5, bg="pink", fg="black")
myb.place(x=560, y=310)
myb.bind("<Button-1>", handle_click)
myb.bind("<Enter>", on_enter)
myb.bind("<Leave>", on_out)


# create a combobox
selected_case = tk.StringVar()
case_cb = ttk.Combobox(master=root, textvariable=selected_case)
case_cb['values'] = cases
case_cb.current(0)
case_cb['state'] = 'readonly'  # normal
statelabel = tk.Label(master=root, text="case: ")
statelabel.place(x=500, y=100)
case_cb.place(x=610, y=100)


# DCN-ip
DCN_lb = tk.Label(master=root, text="DCN-ip: ")
DCN_lb.place(x=500, y=140)
DCN_tx = tk.Text(master=root, width=15, height=1)
DCN_tx.place(x=610, y=140)

# customer
WO_lb = tk.Label(master=root, text="customer - deal: ")
WO_lb.place(x=500, y=180)
WO_tx = tk.Text(master=root, width=35, height=1)
WO_tx.place(x=610, y=180)

root.mainloop()
