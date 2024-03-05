import requests
import tkinter as tk
from tkinter import ttk

class WOselected:
    """
    Lleva el control de la WO a cambiar
    """
    def __init__(self):
        self.id = ''     # WO id number
        self.name = tk.StringVar()   # WO name
        self.name.trace('w', self.wo_display_label)
        self.name_short = tk.StringVar() # WO name organizado con saltos de linea
        self.change_result = tk.StringVar()  # WO resultado de el cambio
        self.change_result.set('...')


    def wo_display_label(self, *args):
        """
        Organiza el nombre en lineas
        """
        line_size = 35
        wo_descr_display = self.name.get()[:line_size]
        for line in range(1, len(self.name.get()) // line_size + 1):
            wo_descr_line = self.name.get()[line * line_size:(line * line_size) + line_size]
            wo_descr_display = '{}\n{}'.format(wo_descr_display, wo_descr_line)
        self.name_short.set(wo_descr_display)



class ComunicaMaximo:
    """
    Se comunica con maximo para obtener y actualizar las wo
    """
    def __init__(self, owner_sccd, user_sccd, pass_sccd, login_url):
        self.wo_list = []    # Almacena las WO sin filtrar
        self.wo_values = []  # Lista con los woid, wo_description, y wo_status
        self.url = login_url
        self.uname = user_sccd
        self.owner = owner_sccd
        self.session = requests.Session()
        self.pass_sccd = pass_sccd

    def update_wo(self):
        """
        Descarga la lista de WO en pending o inprogress y las guarda en el atributo wo_list
        """
        # formato para solicitar todas las WO del usuario en estado Workpending y In progress que no sean task
        url_lref_allwo = '{init_url}oslc/os/sidwo?lean=1&oslc.pageSize=60&oslc.select=*&oslc.' \
                         'where=owner="{uname}"and status IN ["WORKPENDING","INPRG","QUEUED"]and istask=false'. \
            format(uname=self.owner, init_url=self.url)
        current_wo_list = []                               # Almacena las WO sin filtrar
        try:
            self.session.get(self.url, auth=(self.uname, self.pass_sccd))  # Crea una conexión a SCCD
            response_allwo = self.session.get(url_lref_allwo)  # Recibe todas las WO
            print(response_allwo)
            data_allwo = response_allwo.json()                 # Todas las WO en formato JSON
            tamano = len(data_allwo['member'])
            for wo in range(tamano):                           # llena la lista de WO
                current_wo_list.append(data_allwo['member'][wo])
        except:
            show_error()
        self.wo_list = current_wo_list

    def changer(self, worder, my_state, t1, t2, add_log):
        """
        Se comunica con SCCD para cambiar el estado de la WO
        :param worder: WO a cambiar
        :param my_state: Estado en que se quiere dejar la WO
        :param t1: Titulo del log
        :param t2: Descripción del log
        :param add_log: Bool que define se va a adicionar un log
        """
        url_lref_wo = '{init_url}oslc/os/sidwo?lean=1&oslc.select=*&oslc.where=wonum="{wo}"'.format(wo=worder.id,
                                                                                                   init_url=self.url)
        try:
            self.session.get(self.url, auth=(self.uname, self.pass_sccd))
            response_wo = self.session.get(url_lref_wo)
            data_wo = response_wo.json()
            href_str = data_wo['member'][0]['href']
            href_post = href_str+'?lean=1'
        except:
            show_error()

        myheaders = {
            'x-method-override': 'PATCH',
            'patchtype': 'MERGE',
            'Content-Type': 'application/json',
            'properties': '*'
        }

        jedi = {
            "worklog": [
                {
                    "description": "" + t1,
                    "logtype": "CLIENTNOTE",
                    "description_longdescription": "" + t2
                }
            ]
        }

        req1 = self.session.post(href_post, headers=myheaders, json={"status": my_state})
        print("post op1",req1)
        info_message = '{}: '.format(worder.id)
        if req1.status_code == 200:
            info_message = info_message + 'New Status applied'
        else:
            info_message = info_message + 'ERROR changing state'
        if add_log:
            print("create new log")
            print(jedi)
            req2 = self.session.post(href_post, headers=myheaders, json=jedi)
            print("post op2:", req2)
            if req2.status_code == 200:
                info_message = info_message + ' | New log saved'
            else:
                info_message = info_message + ' | ERROR creating log'
        print(info_message)


def show_error():
    """
           Muestra la ventana de error"
    """
    error_win = tk.Tk()
    error_text = tk.Label(error_win, text='Error procesing your request\n'
                                          'please return to init and run the Update Status function again\n'
                                          'if the problem continue, please contact your administrator')
    ok_button = tk.Button(error_win, text="OK", width=5, height=2, command=lambda: error_win.destroy())
    error_text.pack()
    ok_button.pack()
    error_win.mainloop()

def state_change(root, owner_sccd, user_sccd, pass_sccd, login_url):
    """
    Funcion principal de la interface con cambio de estado de la WO
    """
    comm = ComunicaMaximo(owner_sccd, user_sccd, pass_sccd, login_url)         # crea instancia para comunicarse con maximo
    wo_selected_list = []
    message_selected = tk.StringVar()
    def fill_info():
        patrones_borrar = ["NEW SERVICE", "SIDIP", "NEW PROJECT", "IP", "(SIDIP)", "SID-IP", "NEW SERVICE"]

        wo_values = []  # obtiene los woid, wo_description, y wo_status
        for wo_row in range(len(comm.wo_list)):
            descr_mod = "{}".format(comm.wo_list[wo_row]['description'][0:100]).upper().replace('-', ' ')
            for eliminar in patrones_borrar:
                descr_mod = descr_mod.replace(eliminar, '')
            wo_values.append({'woid': "{}".format(comm.wo_list[wo_row]['wogroup']),
                              'wo_descr': descr_mod.strip(),
                              'wo_status': "{}".format(comm.wo_list[wo_row]['status'])})
        return wo_values

    def select_wo_list():
        """
        Funcion para actulizar la lista de WO actualmente seleccionadas
        """
        wo_selected_list.clear()
        for wo_check_ind in wo_box_list:
            if wo_check_ind.get() >= 0:
                wo_checked = WOselected()
                wo_checked.id = comm.wo_values[wo_check_ind.get()]['woid']
                wo_checked.name.set(comm.wo_values[wo_check_ind.get()]['wo_descr'])
                wo_selected_list.append(wo_checked)
            else:
                continue
        print("\nWOs a cambiar: ", end=" ")
        for wo_in_list in wo_selected_list:
            print(wo_in_list.id, end=" ")
        # Create text with the selected WOs
        mess_current_wos = '{} WO selected\n'.format(len(wo_selected_list))
        for current_selected_wo in wo_selected_list:
            mess_current_wos = mess_current_wos + '\u2022' + current_selected_wo.name_short.get() + '\n'
        message_selected.set(mess_current_wos)

    def state_changed(event):
        for current_wo in wo_selected_list:
            msg = "la WO # " + str(current_wo.id) + " cambiara su estado a: " + state_cb.get()
            print("\n", msg)

    def change_title(event):
        titleText.delete("1.0", "end")
        titleText.insert("1.0", selected_title.get())
        bodyText.delete("1.0", "end")
        bodyText.insert("1.0", selected_title.get())

    def handle_click_ce():
        if len(titleText.get("1.0", "end-1c")) == 0:
            ttext = "title_default"
            print(ttext)
        else:
            ttext = titleText.get("1.0", "end-1c")
            print(ttext)
        if len(bodyText.get("1.0", "end-1c")) == 0:
            btext = "body_default"
            print(btext)
        else:
            btext = bodyText.get("1.0", "end-1c")
            print(btext)
        for current_wo in wo_selected_list:
            comm.changer(current_wo, state_cb.get(), ttext, btext, wrlog_value.get())
        handle_click_update()

    def handle_click_update():
        print("actualizar todas la wo")
        comm.update_wo()
        comm.wo_values = fill_info()
        draw_wolist()
        draw_title()
        select_wo_list()

    def handle_click_to_workpending():
        print("change all to workpending")
        for wo in range(len(comm.wo_values)):
            if comm.wo_values[wo]['wo_status'] != 'WORKPENDING':
                wo_changing = WOselected()
                wo_changing.id = comm.wo_values[wo]['woid']
                comm.changer(wo_changing, 'WORKPENDING', '', '', False)
                print("cambiando la WO {}".format(wo_changing.id))
            else:
                print("la WO {} ya esta en WORKPENDING".format(comm.wo_list[wo]['wogroup']))
        select_wo_list()
        handle_click_update()

    def hand_click_order(keyval, rev):
        print("ordenando")
        order_list = sorted(comm.wo_values, key=lambda d: d[keyval], reverse=rev)
        comm.wo_values = order_list
        draw_wolist()
        draw_title()
        select_wo_list()

    def copy_clipboard(textcp):
        root.clipboard_clear()
        root.clipboard_append(textcp)

    def searchChange(event):

        cadena = search_text.get("1.0", "end").replace("\n", "").upper()
        print(cadena)
        for i in range(len(list_label_wo)):
            if len(cadena) >= 3 and cadena in comm.wo_values[i]['wo_descr'].upper():
                list_label_wo[i][0].config(bg='yellow')
                list_label_wo[i][1].config(bg='yellow')
                list_label_wo[i][2].config(bg='yellow')
                list_label_wo[i][3].config(bg='yellow')
                list_label_wo[i][4].config(bg='yellow')
            else:
                list_label_wo[i][0].config(bg='white smoke')
                list_label_wo[i][1].config(bg='white smoke')
                list_label_wo[i][2].config(bg='white smoke')
                list_label_wo[i][3].config(bg='white smoke')
                list_label_wo[i][4].config(bg='white smoke')

    comm.update_wo()

    # Creacion de los frame derecho e izquierdo
    root.columnconfigure(0, weight=1, minsize=40)
    root.columnconfigure(1, weight=1, minsize=10)
    root.rowconfigure(0, weight=1, minsize=2)
    root.rowconfigure(1, weight=1, minsize=10)
    frm_left = tk.Frame(master=root)
    frm_left.grid(row=1, column=0, sticky="nsew")
    frm_right = tk.Frame(master=root)
    frm_right.grid(row=1, column=1, sticky="new", padx=(3, 0))
    frm_right.columnconfigure(0, weight=1, minsize=10)
    frm_right.columnconfigure(1, weight=1, minsize=10)
    frm_left.columnconfigure(0, weight=1, minsize=10)
    frm_left.columnconfigure(1, weight=1, minsize=10)
    frm_left.columnconfigure(2, weight=1, minsize=10)
    frm_left.columnconfigure(3, weight=1, minsize=10)
    frm_left.columnconfigure(4, weight=1, minsize=10)
    frm_left.config(bg='white smoke')

    wo_selected = tk.IntVar(value=0)    # LLeva el registro de la WO seleccionada en la interfaz
    list_label_wo = []
    wo_box_list = []

    def draw_wolist():
        """
        Dibuja la lista de WO en el GUI y asigna los botones de selección
        """
        worders = comm.wo_values
        list_label_wo.clear()
        for widgets in frm_left.winfo_children():    # borra lista actual
            widgets.destroy()
        for wo_row in range(len(worders)):    # crea la interfaz con las WO
            wo_box_list.append(tk.IntVar(value=-1))
            frm_left.rowconfigure(wo_row + 1, weight=1, minsize=1)
            label_wo_id = tk.Label(master=frm_left, text=worders[wo_row]['woid'], bg='white smoke')
            but_cpwo = tk.Button(master=frm_left, text='c', width=1, height=1, bg='white smoke',
                                 command=lambda wo_pass=worders[wo_row]['woid']: copy_clipboard(wo_pass))
            label_wo_desc = tk.Label(master=frm_left, text=worders[wo_row]['wo_descr'], bg='white smoke')
            label_wo_status = tk.Label(master=frm_left, text=worders[wo_row]['wo_status'], bg='white smoke')
            box_btn = tk.Checkbutton(master=frm_left, text="# {}".format(wo_row), variable=wo_box_list[wo_row], onvalue=wo_row,
                                     offvalue=-1, command=select_wo_list)
            list_label_wo.append((label_wo_id, but_cpwo, label_wo_desc, label_wo_status, box_btn))
            box_btn.grid(row=wo_row+1, column=0, sticky="nswe")
            label_wo_id.grid(row=wo_row+1, column=1, sticky="we")
            but_cpwo.grid(row=wo_row+1, column=2, sticky="w")
            label_wo_desc.grid(row=wo_row+1, column=3, sticky="w")
            label_wo_status.grid(row=wo_row+1, column=4)

    def draw_title():
        """
        Dibujar los titulos de la lista de WO
        """
        woval = comm.wo_values
        frm_left.rowconfigure(0, weight=1, minsize=1)
        frm_title_woid = tk.Frame(master=frm_left)
        frm_title_woid.grid(row=0, column=1)
        frm_title_des = tk.Frame(master=frm_left)
        frm_title_des.grid(row=0, column=3)
        frm_title_stat = tk.Frame(master=frm_left)
        frm_title_stat.grid(row=0, column=4)
        but_woid_down = tk.Button(master=frm_title_woid, text="\u2193", width=1, height=1, command=lambda w=woval, k='woid',
                                                                                                     r=False: hand_click_order(k,r))
        but_woid_up = tk.Button(master=frm_title_woid, text="\u2191", width=1, height=1, command=lambda w=woval, k='woid',
                                                                                                   r=True: hand_click_order(k, r))
        but_desc_down = tk.Button(master=frm_title_des, text="\u2193", width=1, height=1, command=lambda w=woval, k='wo_descr',
                                                                                                     r=False: hand_click_order(k, r))
        but_desc_up = tk.Button(master=frm_title_des, text="\u2191", width=1, height=1, command=lambda w=woval, k='wo_descr',
                                                                                                   r=True: hand_click_order(k, r))
        but_status_down = tk.Button(master=frm_title_stat, text="\u2193", width=1, height=1, command=lambda w=woval, k='wo_status',
                                                                                                       r=False: hand_click_order(k, r))
        but_status_up = tk.Button(master=frm_title_stat, text="\u2191", width=1, height=1, command=lambda w=woval, k='wo_status',
                                                                                                     r=True: hand_click_order(k, r))
        woid_title = tk.Label(master=frm_title_woid, text='WO ID', bg='white smoke')
        wodes_title = tk.Label(master=frm_title_des, text='Description', bg='white smoke')
        wostat_title = tk.Label(master=frm_title_stat, text='Status', bg='white smoke')
        woid_title.grid(row=0, column=0, sticky="we")
        but_woid_down.grid(row=0, column=1)
        but_woid_up.grid(row=0, column=2)
        wodes_title.grid(row=0, column=0, sticky="w")
        but_desc_down.grid(row=0, column=1)
        but_desc_up.grid(row=0, column=2)
        wostat_title.grid(row=0, column=0)
        but_status_down.grid(row=0, column=1)
        but_status_up.grid(row=0, column=2)

    comm.wo_values = fill_info()
    draw_wolist()
    draw_title()
    select_wo_list()

    frm_right_up = tk.Frame(master=frm_right)
    frm_right_up.grid(row=0, column=0, sticky="new")
    frm_right_up.columnconfigure(0, weight=1, minsize=10)
    frm_right_up.rowconfigure(0, weight=1, minsize=10)
    frm_right_up.rowconfigure(1, weight=1, minsize=10)
    frm_right_up.rowconfigure(2, weight=1, minsize=10)
    frm_right_up.rowconfigure(3, weight=1, minsize=10)
    frm_right_up.rowconfigure(4, weight=1, minsize=10)
    frm_right_up.rowconfigure(5, weight=1, minsize=10)
    frm_right_up.rowconfigure(6, weight=1, minsize=10)
    frm_right_up.rowconfigure(7, weight=1, minsize=10)
    frm_right_up.rowconfigure(8, weight=1, minsize=10)
    frm_right_down = tk.Frame(master=frm_right)
    frm_right_down.grid(row=1, column=0, sticky="new")

    # search_text
    searchlabel = tk.Label(master=frm_right_up, text="Search: ")
    searchlabel.grid(row=0, column=0, pady=2, sticky=tk.E)
    search_text = tk.Text(master=frm_right_up, width=15, height=1)
    search_text.grid(row=0, column=1, sticky=tk.W, pady=2)
    search_text.bind('<KeyRelease>', searchChange)

    # create a combobox
    states = ('INPRG', 'WORKPENDING')
    selected_state = tk.StringVar()
    state_cb = ttk.Combobox(master=frm_right_up, textvariable=selected_state)
    state_cb['values'] = states
    state_cb['state'] = 'readonly'
    state_cb.current(1)
    state_cb.grid(row=1, column=0, columnspan=2)
    state_cb.bind('<<ComboboxSelected>>', state_changed)

    # Create checkbox aplicar logs
    wrlog_value = tk.BooleanVar()
    wrlog_value.set(True)
    wrlog_chbutt = ttk.Checkbutton(master=frm_right_up, text='Create new log', variable=wrlog_value)
    wrlog_chbutt.grid(row=2, column=0, columnspan=2)

    # Create log title box
    titles = ('---',
              'Se Asigna Especialista de SID-IP',
              'Pendiente KO Interno',
              'Pendiente KO Externo',
              'Se Realiza KO Interno',
              'Se Realiza KO Externo',
              'Se Asigna IP de Gestion',
              'Se Envia Plantilla',
              'Se realiza PEM SID-IP y Se Informa al PM.',
              'Se confirma Operatividad con Cliente',
              'Se adiciona a Forticloud',
              'Se Ingresa a Radius',
              'Se crea Tarea a CSCNET',
              'Se crea Tarea a CSCMON',
              'Se Entrega a Soporte',
              'Se Finaliza Actividades de SID-IP',
              'Se cambian los Recursos en la PEM.',
              'PEM empezo despues de lo programado'
              )
    selected_title = tk.StringVar()
    titlelabel = tk.Label(master=frm_right_up, text="Title: ")
    titlelabel.grid(row=3, column=0, sticky=tk.E)
    title_cb = ttk.Combobox(master=frm_right_up, textvariable=selected_title)
    title_cb['values'] = titles
    title_cb['state'] = 'readonly'
    title_cb.current(0)
    title_cb.grid(row=3, column=1, sticky=tk.W)
    title_cb.bind('<<ComboboxSelected>>', change_title)
    titleText = tk.Text(master=frm_right_up, width=30, height=1)
    titleText.grid(row=4, column=1, sticky=tk.W)

    # Create log description box
    bodylabel = tk.Label(master=frm_right_up, text="Body: ")
    bodylabel.grid(row=5, column=0, sticky=tk.E)
    bodyText = tk.Text(master=frm_right_up, width=30, height=6)
    bodyText.grid(row=5, column=1, sticky=tk.W)

    but_changestate = tk.Button(master=frm_right_up, text="Apply Change", width=14, height=2, command=handle_click_ce)  # boton para aplicar cambio de estado
    but_changestate.grid(row=6, column=0, columnspan=2)

    but_update = tk.Button(master=frm_right_up, text="Update", width=10, height=2, command=handle_click_update)  # boton para actualizar estados
    but_update.grid(row=7, column=0, columnspan=2)

    but_changeall = tk.Button(master=frm_right_up, text="All Workpending", width=16, height=2, command=handle_click_to_workpending)  # boton para actualizar todas a workpendig
    but_changeall.grid(row=8, column=0, columnspan=2)

    frm_right_down.columnconfigure(0, weight=1, minsize=10)
    frm_right_down.rowconfigure(0, weight=1, minsize=10)

    # Show list of selected WOs
    selectedlabel = tk.Label(master=frm_right_down, textvariable=message_selected)
    selectedlabel.grid(row=0, column=0)

    root.mainloop()

if __name__ == "__main__":
    user_sccd = "USUARIO"  # Usuario SCCD de prueba
    pass_sccd = "CONTRASEÑA"  # Contraseña SCCD de prueba
    url_sccd = 'https://servicedesk.cwc.com/maximo/'
    root_win = tk.Tk()

    state_change(root_win, user_sccd, user_sccd, pass_sccd, url_sccd)
