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
import cisco_SW
import cisco_SG300

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))



def handle_click2(event):
    print(var1.get())
    send_user=""
    send_password=""
    credentials=[]
    if var1.get() == 0:
        print("username :"+user_tb.get("1.0", "end-1c"))
        print("password :"+pass_tb.get())
        send_user=user_tb.get("1.0", "end-1c")
        send_password=pass_tb.get()
        print("private_radius_user")
        print("private_radius_password")
    else:
        print("no radius credentials..")
        send_user="sid-ip"
        send_password="sid-cw-bus1n3ss"
        print(send_user)
        print(send_password)
    
    credentials.append(send_user)
    credentials.append(send_password)
    print(credentials)
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


    if case_cb.get() == 'fortinet-vdoms':
        print('vdoms')
        fortinet_atp.DeviceScrapping(DCN_tx.get(
            "1.0", "end-1c"), WO_tx.get("1.0", "end-1c"), application_path,credentials)
    elif case_cb.get() == 'DIA':
        print('DIA')
        DIA.DeviceScrapping(DCN_tx.get(
            "1.0", "end-1c"), WO_tx.get("1.0", "end-1c"), application_path,credentials)
    elif case_cb.get() == 'cisco RT':
        print('cisco RT')
        RT_cisco.Brain(DCN_tx.get(
            "1.0", "end-1c"), WO_tx.get("1.0", "end-1c"), application_path,credentials)
    elif case_cb.get() == 'cisco SW':
        print('cisco SW')
        cisco_SW.DeviceScrapping(DCN_tx.get(
            "1.0", "end-1c"), WO_tx.get("1.0", "end-1c"), application_path,credentials)
    elif case_cb.get() == 'cisco SG300':
        print('cisco SG300')
        cisco_SG300.DeviceScrapping(DCN_tx.get(
            "1.0", "end-1c"), WO_tx.get("1.0", "end-1c"), application_path,credentials)
    

def on_enter(event):
    myb1.configure(relief="sunken")


def on_out(event):
    myb1.configure(relief="raised")

'''
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
    
    if len(valid_customer) != 0:
        validate_name = True
    else:
        validate_name = False
        messagebox.showinfo(
            "message", "customer name must be like 'CUSTOMER NAME-DEALCODE' format")


    if case_cb.get() == 'fortinet-vdoms':
        print('vdoms')
        fortinet_atp.DeviceScrapping(DCN_tx.get(
            "1.0", "end-1c"), WO_tx.get("1.0", "end-1c"), here)
    elif case_cb.get() == 'DIA':
        print('DIA')
        DIA.DeviceScrapping(DCN_tx.get(
            "1.0", "end-1c"), WO_tx.get("1.0", "end-1c"), here)
    elif case_cb.get() == 'cisco RT':
        print('cisco RT')
        RT_cisco.Brain(DCN_tx.get(
            "1.0", "end-1c"), WO_tx.get("1.0", "end-1c"), here)
'''

root = tk.Tk(className=" ATP_GUI")
root.geometry("1300x400")
cases = ('fortinet-vdoms', 'DIA', 'cisco RT','cisco SW','cisco SG300')

# go button
'''
myb = tk.Button(text="Send", width=10, height=5, bg="pink", fg="black")
myb.place(x=560, y=310)
myb.bind("<Button-1>", handle_click2)
myb.bind("<Enter>", on_enter)
myb.bind("<Leave>", on_out)
'''


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


# newcode
def print_selection():
    if var1.get() == 1:
        user_label.place_forget()
        user_tb.place_forget()
        pass_label.place_forget()
        pass_tb.place_forget()

    else:
        user_label.place(x=610, y=220)
        user_tb.place(x=650, y=220)
        pass_label.place(x=610, y=240)
        pass_tb.place(x=650, y=240)
        


var1 = tk.IntVar()
check_box = tk.Checkbutton(master=root, text="enable RADIUS",
                           variable=var1, onvalue=0, offvalue=1, command=print_selection)
check_box.place(x=610, y=200)

user_label = tk.Label(master=root, text="user :")
user_label.place(x=610, y=220)
user_tb = tk.Text(master=root, width=15, height=1)
user_tb.place(x=650, y=220)

pass_label = tk.Label(master=root, text="pass :")
pass_label.place(x=610, y=240)
pass_tb = tk.Entry(width=15,show='*')
pass_tb.place(x=650, y=240)





        
        


myb1 = tk.Button(text="Lets Go!", width=10, height=5, bg="pink", fg="black")
myb1.place(x=700, y=310)
myb1.bind("<Button-1>", handle_click2)


root.mainloop()
