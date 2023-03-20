import requests
from tkinter import *
from tkinter import messagebox
import tkinter as tk

def init_var(envir):
    """
    Define las variables iniciales
    :param envir: Ambiente GUI principal
    :return: (root_win, user_sccd, pass_sccd, url_sccd)
    """
    user_sccd = envir.get_user_sccd()
    pass_sccd = envir.get_pass_sccd()
    owner_sccd = envir.get_owner_sccd()
    url_sccd = envir.get_urlsccd()
    root_win = envir.get_work_area()

    return root_win, owner_sccd, user_sccd, pass_sccd, url_sccd

mylist = []
labelList = []

def textHasChanged(event):
    cadena = new_owner.get("1.0", "end-1c").replace("\n", "")

    if len(cadena) > 0:
        new_owner_group.configure(state='disabled')
        new_owner_group.config(bg="grey")
    else:
        new_owner_group.configure(state='normal')
        new_owner_group.config(bg="white")


def textHasChanged2(event):
    cadena = new_owner_group.get("1.0", "end-1c").replace("\n", "")

    if len(cadena) > 0:
        new_owner.configure(state='disabled')
        new_owner.config(bg="grey")
    else:
        new_owner.configure(state='normal')
        new_owner.config(bg="white")


def call_change_owner(environment):
    """
    Funcion principal para el cambio de owner de la WO
    """
    root_win, initial_owner, user, password, url = init_var(environment)

    session = requests.Session()
    session.get(url, auth=(user, password))

    def QuerySCCD(aim):
        request = session.get(aim)
        print(str(request))
        return (request.json())

    def changeOwner(wo):
        subs = "200"

        target3 = "https://servicedesk.cwc.com/maximo/oslc/os/sidwo?lean=1&oslc.select=*&oslc.where=wonum=" + '"' + wo + '"'
        data3 = QuerySCCD(target3)
        href = data3['member'][0]

        href_str = href['href']
        url_editable = href_str.replace("http://localhost", "https://servicedesk.cwc.com") + '?lean=1'
        print(href_str)
        print(url_editable)

        myheaders = {
            'x-method-override': 'PATCH',
            'patchtype': 'MERGE',
            'Content-Type': 'application/json',
            'Authorization': 'YW1vbGFubzpNM2dhZGV0aDIwMzYq',
            'properties': '*'
        }

        jedi = {
            "worklog": [
                {

                    "description": "CAMBIO DE OWNER  BY ATOM",
                    "logtype": "CLIENTNOTE",
                    "description_longdescription": "CAMBIO DE OWNER BY ATOM"
                }
            ]

        }

        if len(new_owner.get("1.0", "end-1c").replace("\n", "")) > 0:
            zeta = new_owner.get('1.0', 'end-1c').upper()
            print("got owner")
            req2 = session.post(url_editable, headers=myheaders, json={"owner": zeta})
            print("post op:", req2)
            req3 = session.post(url_editable, headers=myheaders, json=jedi)
            print("post op2:", req3)
        else:
            zeta = new_owner_group.get('1.0', 'end-1c').upper()
            print("got owner group")
            req2 = session.post(url_editable, headers=myheaders, json={"ownergroup": zeta})
            print("post op:", req2)
            req3 = session.post(url_editable, headers=myheaders, json=jedi)
            print("post op2:", req3)
            new_window.destroy()

        if subs in str(req2) and subs in str(req3):
            print("true")
            messagebox.showinfo("message", "Change done successfully!...")

        else:
            print("false")

    def searchChange(event):
        cadena = search_wo.get("1.0", "end").replace("\n", "").upper()

        for item in labelList:
            if len(cadena) >= 3 and cadena in item['text'].upper():
                item.config(bg="yellow")
            else:
                item.config(bg="#eaece9")

    def which_button(m):
        print(m.split()[0], " : m()[0]")
        workOrder = m.split()[0]
        target = url + "oslc/os/sidwo?lean=1&oslc.select=*&oslc.where=wonum=" + '"' + m.split()[0] + '"'
        info = QuerySCCD(target)
        myArray = info['member'][0]
        print(myArray['wogroup'])

        global label1, new_owner, new_owner_group, new_window
        new_window = tk.Toplevel(root_win)
        new_window.geometry("750x250")
        new_window.title("Change owner")

        label1 = tk.Label(new_window, text="enter new owner: ", font=('Helvetica 10 bold'))
        label1.grid(sticky=W, row=0, column=0)

        new_owner = tk.Text(new_window, width=15, height=1)
        new_owner.grid(sticky=W, row=0, column=1)
        new_owner.bind('<KeyRelease>', textHasChanged)

        tk.Label(new_window, text="enter new owner group: ", font=('Helvetica 10 bold')).grid(sticky=W, row=1, column=0)
        global new_owner_group
        new_owner_group = tk.Text(new_window, width=15, height=1)
        new_owner_group.grid(sticky=W, row=1, column=1)
        new_owner_group.bind('<KeyRelease>', textHasChanged2)
        tk.Button(new_window, text="submit", width=12, height=1, bg="white", fg="black",
                  command=lambda wo=workOrder: changeOwner(wo)).grid(sticky=W, row=3, column=0)

    def query_handler():
        print("current total child :", frm_left.winfo_children())
        if len(frm_left.winfo_children()) > 0:
            for widget in frm_left.winfo_children():
                widget.destroy()
                del mylist[:]
                del labelList[:]

        search_wo.config(state="normal")
        mystring = search_owner.get("1.0", "end-1c").upper()
        lookup_list = mystring.split()
        print(str(lookup_list).replace("'", '"').replace(", ", ","))

        target = url + 'oslc/os/sidwo?lean=1&oslc.pageSize=60&oslc.select=*&oslc.where=ownergroup IN ' + str(
            lookup_list).replace("'", '"').replace(", ", ",") + ' and status IN ["WORKPENDING","INPRG","QUEUED"]and istask=false'
        target2 = url + 'oslc/os/sidwo?lean=1&oslc.pageSize=60&oslc.select=*&oslc.where=owner IN ' + str(
            lookup_list).replace("'", '"').replace(", ", ",") + ' and status IN ["WORKPENDING","INPRG","QUEUED"]and istask=false'

        print(target)
        print(target2)
        data_ = QuerySCCD(target)
        data_2 = QuerySCCD(target2)
        tamaño = len(data_['member'])
        tamaño2 = len(data_2['member'])
        for i in range(tamaño):
            mylist.append(data_['member'][i])
        for i in range(tamaño2):
            mylist.append(data_2['member'][i])

        for item in range(0, len(mylist)):
            pretext = "{:<10} : {}"
            frm_left.rowconfigure(item, weight=1, minsize=1)
            r = tk.Label(frm_left, text=pretext.format(mylist[item]['wogroup'],
                                                   mylist[item]['description'][0:55].replace("New Service", "").replace(
                                                       "SIDIP", "").replace("New Project", "").replace("-", "").replace(
                                                       "IP", "").replace("(SIDIP)", "").upper().strip(),
                                                   mylist[item]['wonum'],
                                                   justify=LEFT))
            b = Button(frm_left, text="" + r.cget("text"), width=70, height=1, bg="white", fg="black",
                       command=lambda m=r.cget("text"): which_button(m), anchor="w")
            labelList.append(b)
            b.grid(row=item, column=0)

        environment.update_canvas()

    # Creacion de los frame derecho e izquierdo
    root_win.columnconfigure(0, weight=2, minsize=40)
    root_win.columnconfigure(1, weight=1, minsize=10)
    root_win.rowconfigure(0, weight=1, minsize=40)
    frm_left = tk.Frame(master=root_win, bg='#eaece9')
    frm_right = tk.Frame(master=root_win)
    frm_left.columnconfigure(0, weight=1, minsize=10)
    frm_left.grid(row=0, column=0, sticky="nsew")
    frm_right.grid(row=0, column=1, sticky="new", padx=(3, 0))
    frm_right.rowconfigure(0, weight=1, minsize=2)
    frm_right.rowconfigure(1, weight=1, minsize=2)
    frm_right.rowconfigure(2, weight=1, minsize=2)
    frm_right.columnconfigure(0, weight=1, minsize=2)
    frm_right.columnconfigure(1, weight=1, minsize=2)

    # search pm
    searchlabel = tk.Label(master=frm_right, text="Search : ")
    searchlabel.grid(row=0, column=0, sticky="e")
    search_owner = tk.Text(master=frm_right, width=15, height=1)
    search_owner.grid(row=0, column=1, sticky="w")

    mibo = tk.Button(master=frm_right, text="lookup", width=10, height=1, bg="white", fg="black", command=query_handler)
    mibo.grid(row=1, column=1, sticky="w")

    searchlabel2 = tk.Label(master=frm_right, text="lookup :")
    searchlabel2.grid(row=2, column=0, sticky="e")
    search_wo = tk.Text(master=frm_right, width=15, height=1, state='disabled')
    search_wo.grid(row=2, column=1, sticky="w")
    search_wo.bind('<KeyRelease>', searchChange)

    root_win.mainloop()

if __name__ == "__main__":
    call_change_owner()
