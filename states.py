import requests
import tkinter as tk
from tkinter import ttk
import time
import threading
from playsound import playsound

import timekeeper

stop_check_time = False

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
        Funcion para actualizar la lista de WO actualmente seleccionadas
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
        if len(wo_selected_list) > 1:
            wos_selected_lb.config(fg='red')
        else:
            wos_selected_lb.config(fg='black')

    def clear_wo_checkboxes():
        list_label_wo
        for list_item in list_label_wo:
           list_item[4].deselect()
        select_wo_list()

    def state_changed(event):
        for current_wo in wo_selected_list:
            msg = "la WO # " + str(current_wo.id) + " cambiara su estado a: " + state_cb.get()
            print("\n", msg)

    def select_log(event):
        log_option_map = {'REVISION PRELIMINAR DEL PROYECTO': 'P00. REVISION PRELIMINAR DEL PROYECTO',
                          'KO INTERNO (KOI)': 'P01. KO INTERNO (KOI)',
                          'KO EXTERNO (KOE)': 'P02. KO EXTERNO (KOE)',
                          'PLANTILLA ALISTAMIENTO': 'P03. PLANTILLA ALISTAMIENTO',
                          'PEM (EJECUCION)': 'P04. PEM (EJECUCION)',
                          'DOCUMENTACION (PREPARACION)': 'P05. DOCUMENTACION (PREPARACION)',
                          'REUNION SEGUIMIENTO - INTERNA': 'P06. REUNION SEGUIMIENTO - INTERNA',
                          'REUNION SEGUIMIENTO - CLIENTE': 'P07. REUNION SEGUIMIENTO - CLIENTE',
                          'CSC (CREACION TAREA)': 'P08. CSC (CREACION TAREA)',
                          'ESPECIALISTA ASIGNADO': 'N01. ESPECIALISTA ASIGNADO',
                          'PLANTILLA ENVIADA': 'N02. PLANTILLA ENVIADA',
                          'ACTIVIDADES FINALIZADAS': 'N03. ACTIVIDADES FINALIZADAS',
                          'CSC (ENTREGA ACEPTADA)': 'N04. CSC (ENTREGA ACEPTADA)',
                          'WO SIN ACTIVIDAD': 'N05. WO SIN ACTIVIDAD',
                          'WO CANCELADA': 'N06. WO CANCELADA',
                          'KOI PENDIENTE': 'N07. KOI PENDIENTE',
                          'KOE PENDIENTE': 'N08. KOE PENDIENTE',
                          'RECURSOS PENDIENTES': 'N09. RECURSOS PENDIENTES',
                          'RECURSOS CAMBIADOS': 'N10. RECURSOS CAMBIADOS',
                          'PEM DEMORADA': 'N11. PEM DEMORADA',
                          'PEM COMPLETA': 'N12. PEM COMPLETA',
                          'EN MONITOREO': 'N13. EN MONITOREO',
                          'FORTICLOUD AGREGADO': 'N14. FORTICLOUD AGREGADO',
                          'RADIUS AGREGADO': 'N15. RADIUS AGREGADO',
                          'ESCALAMIENTO A TERCERO': 'N16. ESCALAMIENTO A TERCERO',
                          'DEVOLUCION PM x INACTIVIDAD': 'N17. DEVOLUCION PM x INACTIVIDAD',
                          'ENTREGA PARCIAL': 'N18. ENTREGA PARCIAL',
                          'CIERRE WO POR SLA': 'N19. CIERRE WO POR SLA',
                          'INICIO DE VENTANA MTO': 'N20. INICIO DE VENTANA MTO',
                          'FINAL DE VENTANA MTO': 'N21. FINAL DE VENTANA MTO',
                          'SE AÑADEN LICENCIAS': 'N22. SE AÑADEN LICENCIAS',
                          'NOTA/COMENTARIO': 'N23. NOTA/COMENTARIO'
                          }
        titleText.delete("1.0", "end")
        titleText.insert("1.0", log_option_map.get(selected_title.get(), '-'))
        bodyText.delete("1.0", "end")
        bodyText.insert("1.0", log_option_map.get(selected_title.get(), '-'))

    ## Anuncio de error digitando el tiempo


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
            
            ##TIME-CODE##
            
            if state_cb.get() == 'INPRG' and settime_value.get() == True :
                print("horas: ", int(hour_entry.get("1.0", "end-1c")), type(int(hour_entry.get("1.0", "end-1c"))))
                print("minutos: ",int(min_entry.get("1.0", "end-1c")),type(int(min_entry.get("1.0", "end-1c"))))

                if 0 <= int(hour_entry.get("1.0", "end-1c")) <= 8 and 0 <= int(min_entry.get("1.0", "end-1c")) <= 60:

                    if int(hour_entry.get("1.0", "end-1c"))== 0 and int(min_entry.get("1.0", "end-1c")) == 0:
                        tk.messagebox.showinfo("TIME ERROR", "No time to count.")
                    else:
                        comm.changer(current_wo, state_cb.get(), ttext, btext, wrlog_value.get())
                        counters[current_wo.id].count(int(hour_entry.get("1.0", "end-1c")),int(min_entry.get("1.0", "end-1c")))
                else:
                    tk.messagebox.showinfo("TIME ERROR", "The minutes has to be a numeric value between 0 and 60. The hours has to be a numeric value between 0 and 8.")
            else:
                comm.changer(current_wo, state_cb.get(), ttext, btext, wrlog_value.get())
            
        handle_click_update()




    def handle_click_update():
        print("actualizar todas la wo")
        comm.update_wo()
        comm.wo_values = fill_info()
        draw_wolist()
        draw_title()
        select_wo_list()
        clear_wo_checkboxes()

    def handle_click_to_workpending():
        print("change all to workpending")
        for wo in range(len(comm.wo_values)):
            if comm.wo_values[wo]['wo_status'] != 'WORKPENDING':
                wo_changing = WOselected()
                wo_changing.id = comm.wo_values[wo]['woid']
                comm.changer(wo_changing, 'WORKPENDING', '', '', False)
                WO_finish_flag[wo_changing.id]=True
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
        clear_wo_checkboxes()

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
    ##TIME-CODE##
    frm_left.columnconfigure(5, weight=1, minsize=10)

    frm_left.config(bg='white smoke')


    ##TIME-CODE##




    comm.update_wo()
    comm.wo_values = fill_info()
    worders_list = comm.wo_values
    WO_list=[]
    WO_finish_flag={}
    for WO_dic in worders_list:
        WO_list.append(WO_dic['woid'])
        WO_finish_flag[WO_dic['woid']]=False

    counters=timekeeper.generate(WO_list)





    print('WO a trabajar')
    print(counters)

    list_label_wo = [] #Lista de tuplas que contienen los label que irán en cada fila DE WOs
    wo_box_list = [] # Array de IntVar para los valores onvalue/offvalue en forma de tk.IntVar() para el Checkbutton de cada WO
    list_wo_to_change={}

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
            ##TIME-CODE##
            time_left=counters[worders[wo_row]['woid']].tk_time

            wo_finish=WOselected() 
            wo_finish.id=worders[wo_row]['woid']
            list_wo_to_change[worders[wo_row]['woid']]=wo_finish

            label_time = tk.Label(master=frm_left, text="00:00:00", textvariable=time_left, bg='white smoke') #Label que mostrará el tiempo, por defecto tendrá un valor de 00:00:00.
            list_label_wo.append((label_wo_id, but_cpwo, label_wo_desc, label_wo_status, box_btn,label_time))

            box_btn.grid(row=wo_row+1, column=0, sticky="nswe")
            label_wo_id.grid(row=wo_row+1, column=1, sticky="we")
            but_cpwo.grid(row=wo_row+1, column=2, sticky="w")
            label_wo_desc.grid(row=wo_row+1, column=3, sticky="w")
            label_wo_status.grid(row=wo_row+1, column=4)

            ##TIME-CODE##
            label_time.grid(row=wo_row+1, column=5)

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

        ##TIME-CODE##
        frm_tittle_time= tk.Frame(master=frm_left) ## título time
        frm_tittle_time.grid(row=0, column=5)

        but_unchek_all = tk.Button(master=frm_left, text="X", width=1,height=1, command=clear_wo_checkboxes)
        but_unchek_all.grid(row=0, column=0, sticky="w")
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

        ##TIME-CODE##
        time_title = tk.Label(master=frm_tittle_time, text='Time', bg='white smoke') # Título time para los tiempos INPROG

        woid_title.grid(row=0, column=0, sticky="we")
        but_woid_down.grid(row=0, column=1)
        but_woid_up.grid(row=0, column=2)
        wodes_title.grid(row=0, column=0, sticky="w")
        but_desc_down.grid(row=0, column=1)
        but_desc_up.grid(row=0, column=2)
        wostat_title.grid(row=0, column=0)
        but_status_down.grid(row=0, column=1)
        but_status_up.grid(row=0, column=2)

        ##TIME-CODE##
        time_title.grid(row=0, column=0)

        



    comm.wo_values = fill_info()
    draw_wolist()
    draw_title()




    
    ##Función que añade el log al terminar el contador y cambia la WO a workpending

    def counter_finish(wo_finished):
        ttext = "Finished/Finalizado"
        btext = "Finished/Finalizado"
        playsound("alarm.mp3")
        tk.messagebox.showinfo("WO TO WORKPENDING", "The activity time has finished. Please, documentate the WO or set more INPRG time")
        comm.changer(wo_finished, 'WORKPENDING', ttext, btext, True)
        print("La WO pasó a workpending")

    ##Función que revisa cada segundo el valor de los contadores de cada WO y ejecuta la finalización "counter_finish()" una vez el contador llegue a 1

    def check_time():
        while stop_check_time == False: 
            print("Time check")
            for wo, counter in counters.items():   
                print('La WO ', wo, 'Le quedan ', counter.secs_rest, ' Segundos' )
                if counter.secs_rest == 1 or WO_finish_flag[wo]==True:
                    counter.finish()
                    counter_finish(list_wo_to_change[wo])
                    handle_click_update()
                    counter.finish()
                    WO_finish_flag[wo]=False
                else:
                    continue          
            time.sleep(1)

    



    # Crear el hilo
    check_time_thread = threading.Thread(target=check_time)

    

    # Iniciar el hilo
    check_time_thread.start()
 











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

    ##TIME-CODE##
    frm_right_up.rowconfigure(9, weight=1, minsize=10) #new checkbox para aplicar contador
    frm_right_up.rowconfigure(10, weight=1, minsize=10) #new entry minutes
    frm_right_up.rowconfigure(11, weight=1, minsize=10) #new entry hours

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
    state_cb = ttk.Combobox(master=frm_right_up, textvariable=selected_state) #IWORKING
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
    log_options = ('---',
                   'REVISION PRELIMINAR DEL PROYECTO',
                   'KO INTERNO (KOI)',
                   'KO EXTERNO (KOE)',
                   'PLANTILLA ALISTAMIENTO',
                   'PEM (EJECUCION)',
                   'DOCUMENTACION (PREPARACION)',
                   'REUNION SEGUIMIENTO - INTERNA',
                   'REUNION SEGUIMIENTO - CLIENTE',
                   'CSC (CREACION TAREA)',
                   'ESPECIALISTA ASIGNADO',
                   'PLANTILLA ENVIADA',
                   'ACTIVIDADES FINALIZADAS',
                   'CSC (ENTREGA ACEPTADA)',
                   'WO SIN ACTIVIDAD',
                   'WO CANCELADA',
                   'KOI PENDIENTE',
                   'KOE PENDIENTE',
                   'RECURSOS PENDIENTES',
                   'RECURSOS CAMBIADOS',
                   'PEM DEMORADA',
                   'PEM COMPLETA',
                   'EN MONITOREO',
                   'FORTICLOUD AGREGADO',
                   'RADIUS AGREGADO',
                   'ESCALAMIENTO A TERCERO',
                   'DEVOLUCION PM x INACTIVIDAD',
                   'ENTREGA PARCIAL',
                   'CIERRE WO POR SLA',
                   'INICIO DE VENTANA MTO',
                   'FINAL DE VENTANA MTO',
                   'SE AÑADEN LICENCIAS',
                   'NOTA/COMENTARIO'
                   )
    selected_title = tk.StringVar()
    titlelabel = tk.Label(master=frm_right_up, text="Title: ")
    titlelabel.grid(row=3, column=0, sticky=tk.E)
    title_cb = ttk.Combobox(master=frm_right_up, textvariable=selected_title, width=40)
    title_cb['values'] = log_options
    title_cb['state'] = 'readonly'
    title_cb.current(0)
    title_cb.grid(row=3, column=1, sticky=tk.W)
    title_cb.bind('<<ComboboxSelected>>', select_log)
    titleText = tk.Text(master=frm_right_up, width=30, height=1)
    titleText.grid(row=4, column=1, sticky=tk.W)

    # Create log description box
    bodylabel = tk.Label(master=frm_right_up, text="Body: ")
    bodylabel.grid(row=5, column=0, sticky=tk.E)
    bodyText = tk.Text(master=frm_right_up, width=30, height=6)
    bodyText.grid(row=5, column=1, sticky=tk.W)

    but_changestate = tk.Button(master=frm_right_up, text="Apply Change", width=14, height=2, command=handle_click_ce)  # boton para aplicar cambio de estado
    but_changestate.grid(row=6, column=0, columnspan=2)

    but_update = tk.Button(master=frm_right_up, text="Update List", width=10, height=2, command=handle_click_update)  # boton para actualizar estados
    but_update.grid(row=7, column=0, columnspan=2)

    but_changeall = tk.Button(master=frm_right_up, text="All Workpending", width=16, height=2, command=handle_click_to_workpending)  # boton para actualizar todas a workpendig
    but_changeall.grid(row=8, column=0, columnspan=2)



     ##TIME-CODE##
    ### Define timer ###

    settime_value = tk.BooleanVar()
    settime_value.set(False)
    settime_chbutt = ttk.Checkbutton(master=frm_right_up, text='Set time in "INPRG', variable=settime_value)
    

    hourlabel = tk.Label(master=frm_right_up, text="Enter hours: ")
    hour_entry = tk.Text(master=frm_right_up, width=5, height=1)
    minlabel = tk.Label(master=frm_right_up, text="Enter minutes: ")
    min_entry = tk.Text(master=frm_right_up, width=5, height=1)

    settime_chbutt.grid(row=9, column=0, columnspan=2)
    hourlabel.grid(row=10, column=0, sticky=tk.E)
    hour_entry.grid(row=10, column=1, sticky=tk.W)
    minlabel.grid(row=11, column=0, sticky=tk.E)
    min_entry.grid(row=11, column=1, sticky=tk.W)


    frm_right_down.columnconfigure(0, weight=1, minsize=10)
    frm_right_down.rowconfigure(0, weight=1, minsize=10)

    # Show list of selected WOs
    wos_selected_lb = tk.Label(master=frm_right_down, textvariable=message_selected, fg='black')
    wos_selected_lb.grid(row=0, column=0)

    select_wo_list()

    root.mainloop()

if __name__ == "__main__":
    user_sccd = "USUARIO"  # Usuario SCCD de prueba
    pass_sccd = "CONTRASEÑA"  # Contraseña SCCD de prueba
    url_sccd = 'https://servicedesk.cwc.com/maximo/'
    root_win = tk.Tk()

    state_change(root_win, user_sccd, user_sccd, pass_sccd, url_sccd)
