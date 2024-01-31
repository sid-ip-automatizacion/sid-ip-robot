import tkinter
from tkinter import ttk
from pathlib import Path

import llenar_assessment
import config_meraki_sw

"""
Modulo con la interfaz gráfica para las funciones de configuración automática de switches
"""


def exec_gui(root_win, api_key_meraki):
    def clear_work_area():
        """
        limpia el alres de trabajo
        """
        for widgets in root_win.winfo_children():
            widgets.destroy()

    def help_message(section):
        """
        Muestra ventanas con mensajes de ayuda
        """
        messages = {
            'configs_files': "Ingrese los nombres completos (con extensión si es del caso) de los archivos de configuración,"
                             " separados por comas.\n"
                             "El orden de la lista de archivos de configuración debe ser el mismo de la lista de "
                             "archivos de excel.\n"
                             "Los archivos de configuración se deben ubicar en la carpeta:\n\n"
                             "<directorio_de_trabajo>/switch_config_files/\n\n"
                             "siendo <directorio de trabajo> el directorio donde se tiene el programa sid-ip-robot.\n"
                             "Estos archivos de configuracion son archivos de texto que contienen la configuracion de"
                             " los switches, por ejemplo, la salida del comando show run en los switches Cisco",
            'assessment_files': "Ingrese los nombres de los archivos de excel en donde se almacenara la información de "
                                "los switches, separados por comas.\n"
                                "El orden de la lista de archivos de excel debe ser el mismo empleado en la lista de"
                                " archivos de configuración.\n"
                                "Recuerde incluir la extensión .xlsx en el nombre de los archivos.\n"
                                "Los archivos de excel se ubicarán el la carpeta:\n\n"
                                "<directorio_de_trabajo>/assessments/\n\n"
                                "siendo <directorio de trabajo> el directorio donde se tiene el programa sid-ip-robot.\n",
            'plantillas': "Elija la plantilla a usar dependiendo del modelo de switch, o cree la plantilla apropiada en el "
                          "directorio:\n\n"
                          "<directorio_de_trabajo>/sw_model_templates\n\n"
                          "Las plantillas contienen el formato de la configuración original de los switches, y permiten"
                          " identificar la ubicación de los valores de las interfaces a extraer. Por ejemplo en un equipo "
                          "Cisco CBS250 en el archivo de configuración, las interfaces se muestran típicamente de la siguiente "
                          "manera: \n\n"
                          "interface GigabitEthernet1\n"
                          "description PC-Salon1\n"
                          "switchport mode trunk\n"
                          "switchport trunk native vlan 4\n"
                          "switchport trunk allowed vlan 4,10,20\n"
                          "!\n"
                          "En la plantilla se reemplazan los valores a extraer por #VAR_n, siendo un entero entre 1 y 10 "
                          "que identifica el valor a extraer. Así la plantilla para el Cisco CBS250 del ejemplo será\n\n"
                          "interface GigabitEthernet#VAR_1\n"
                          " description #VAR_2\n"
                          " switchport mode #VAR_3\n"
                          " switchport trunk native vlan #VAR_4\n"
                          " switchport trunk allowed vlan #VAR_5\n"
                          "!\n\n"
                          "Adicionalmente en la parte inferior de la plantilla se definen los valores inicio_bloque_interface"
                          " y fin_bloque_interface. Estos valores sirven para identificar donde inicia y donde termina la "
                          "definición de cada interface, para el ejemplo anterior al final de la plantilla se tendrá:\n\n"
                          "#######################################################################\n"
                          "inicio_bloque_interface: interface Gigabit\n"
                          "fin_bloque_interface: !\n\n"
                          "Ya que el texto: interface Gigabit, sirve para identificar el inicio de la configuración de una "
                          "interface, y el texto: !, para identificar su final",
            'asign_var': "Elija el archivo de identificacion de variables de acuerdo a la plantilla a usar o cree uno nuevo "
                         "en el directorio:\n\n"
                         "<directorio_de_trabajo>/var_mapings\n\n"
                         "El archivo a elegir depende de la plantilla empleada y permite asignar a cada variable indicada "
                         "en la plantilla una columna en el archivo de assessment de excel. Por ejemplo si en la planitlla "
                         "tenemos definidas las variables de la siguiente manera:\n"
                         "interface GigabitEthernet#VAR_1\n"
                         " description #VAR_2\n"
                         " switchport mode #VAR_3\n"
                         " switchport trunk native vlan #VAR_4\n"
                         " switchport trunk allowed vlan #VAR_5\n\n"
                         "En el archivo de identificación de variables se podria hcer el match de la siguiente forma:\n\n"
                         "{\n"
                         "  \"variable_names\" :{\n"
                         "    \"port\": \"VAR_1\",\n"
                         "    \"port_mode\": \"VAR_3\",\n"
                         "    \"description\": \"VAR_2\",\n"
                         "    \"native_vlan\": \"VAR_4\",\n"
                         "    \"tag_vlans\": \"VAR_5\",\n"
                         "    \"voice_vlan\": \"\",\n"
                         "    \"stp_guard\": \"\",\n"
                         "    \"poe\": \"\"\n"
                         "  }\n"
                         "}\n\n"
                         "Indicando que el valor definido en la plantilla como #VAR_1 corresponde a la columna 'port' del "
                         "archivo de excel, el definido como #VAR_2 corresponde a la columna 'description', etc.",
            'excel_files_config': "Ingrese los archivos de assessment de excel con la información para configurar los switches "
                                  "meraki.\n"
                                  "Ingrese los valores como una lista separada por comas.\n"
                                  "El orden de la lista de archivos debe ser el mismo de la lista de seriales\n"
                                  "Recuerde incluir la extención .xlsx en el nombre del archivo.\n"
                                  "Los archivos deben estar en el directorio:\n\n"
                                  "<directorio_de_trabajo>/assessments\n\n"
                                  "siendo <directorio_de_trabajo> el directorio donde se encuentra el ejecutable de sid-ip-robot",
            'seriales_sw': "Ingrese los seriales de los switches meraki a configurar.\n"
                           "Ingrese los valores como una lista separada por comas.\n"
                           "El orden de la lista de seriales debe ser el mismo de la lista de archivos de excel con la "
                           "configuración.\n"
        }
        # Mostrar el cuadro de ayuda
        help_window = tkinter.Tk()
        scroll_bar = tkinter.Scrollbar(master=help_window, orient=tkinter.VERTICAL)
        scroll_bar.pack(side=tkinter.RIGHT, fill='y')
        text_widget = tkinter.Text(master=help_window, yscrollcommand=scroll_bar.set, font=('Helvetica', 11))
        text_widget.insert(tkinter.END, messages.get(section, 'nada que mostrar'))
        text_widget.config(state=tkinter.DISABLED)
        scroll_bar.config(command=text_widget.yview)
        text_widget.pack(expand=True, fill=tkinter.BOTH)
        help_window.mainloop()

    class GuiExtractConfig:
        """
        Clase con las funciones para obtener los assessment en excel de las configuraciones en texto
        """
        def __init__(self):
            self.frm = ''
            self.archivos_config_str = ''
            self.plantilla = ''
            self.ini_bloque = ''
            self.fin_bloque = ''
            self.archivos_assessment_str = ''
            self.var_mapping = ''
            self.current_state = tkinter.StringVar()

        def llenar_excel_button(self):
            """
            Programa que corre al presionar el boton de ejecución de la ventana de llenado archivos excel
            """
            archivos_assess_exec = [archiv_str.strip() for archiv_str in self.archivos_assessment_str.get().split(',')]
            config_files = [config.strip() for config in self.archivos_config_str.get().split(',')]
            llenar_assessment.execute_assess(archivos_assess_exec, config_files, self.plantilla, self.var_mapping)
            self.current_state.set("Completed\n"
                                   "Please verify the config files in your /assessments directory ")

        def run_gui(self):
            """
            Ejecuta la interfaz gráfica para extraer los assessments de las configuraciones
            """
            def selecciona_plantilla(event):
                self.plantilla = plantillas_combo.get()

            def selecciona_maping(event):
                self.var_mapping = maping_combo.get()

            clear_work_area()
            self.frm = tkinter.Frame(master=root_win)
            self.frm.grid(row=0, column=0)
            self.frm.rowconfigure(0, weight=1, minsize=10)
            self.frm.rowconfigure(1, weight=1, minsize=10)
            self.frm.rowconfigure(2, weight=1, minsize=10)
            self.frm.rowconfigure(3, weight=1, minsize=10)
            self.frm.rowconfigure(4, weight=1, minsize=10)
            self.frm.rowconfigure(5, weight=1, minsize=10)
            self.frm.rowconfigure(6, weight=1, minsize=10)
            self.frm.columnconfigure(0, weight=1, minsize=10)
            self.frm.columnconfigure(1, weight=1, minsize=10)
            self.frm.columnconfigure(2, weight=1, minsize=10)
            # Titulo
            title_lb = ttk.Label(self.frm, text="Extraer configuracion en Excel", anchor=tkinter.CENTER, font=('Helvetica',12))
            title_lb.grid(row=0, columnspan=3, pady=10)
            # Seleccionar la plantilla a usar
            path_plantillas = Path.cwd().joinpath('sw_model_templates')
            plantillas_names = [plantilla.name for plantilla in path_plantillas.iterdir()]
            plantillas_lb = tkinter.Label(self.frm, text="Seleccione la plantilla a usar")
            plantillas_lb.grid(row=1, column=0, sticky=tkinter.W)
            plantillas_combo = ttk.Combobox(self.frm, state='readonly', values=plantillas_names)
            plantillas_combo.bind("<<ComboboxSelected>>", selecciona_plantilla)
            plantillas_combo.grid(row=1, column=1)
            plantillas_help = tkinter.Button(self.frm, text='?', command=lambda: help_message('plantillas'))
            plantillas_help.grid(row=1, column=2, sticky="we")
            # Seleccionar archivo con mapeo de variables
            path_mapings = Path.cwd().joinpath('var_mapings')
            maping_names = [maping.name for maping in path_mapings.iterdir()]
            maping_lb = tkinter.Label(self.frm, text="Seleccione el archivo de identificacion de variables")
            maping_lb.grid(row=2, column=0, sticky=tkinter.W)
            maping_combo = ttk.Combobox(self.frm, state='readonly', values=maping_names)
            maping_combo.bind("<<ComboboxSelected>>", selecciona_maping)
            maping_combo.grid(row=2, column=1)
            maping_help = tkinter.Button(self.frm, text='?', command=lambda: help_message('asign_var'))
            maping_help.grid(row=2, column=2, sticky="we")
            # Ingresar listado de archivos excel
            self.archivos_assessment_str = tkinter.StringVar(self.frm)
            excel_files_lb = tkinter.Label(self.frm, text="Archivos excel destino (.xlsx)")
            excel_files_lb.grid(row=3, column=0, sticky=tkinter.W)
            excel_files_ent = tkinter.Entry(self.frm, textvariable=self.archivos_assessment_str, width=50)
            excel_files_ent.grid(row=3, column=1, sticky=tkinter.W)
            excel_help = tkinter.Button(self.frm, text='?', command=lambda: help_message('assessment_files'))
            excel_help.grid(row=3, column=2, sticky="we")
            # Ingresar listado de configuraciones
            self.archivos_config_str = tkinter.StringVar(self.frm)
            confi_files_lb = tkinter.Label(self.frm, text="Archivos de configuraciones")
            confi_files_lb.grid(row=4, column=0, sticky=tkinter.W)
            confi_files_ent = tkinter.Entry(self.frm, textvariable=self.archivos_config_str, width=50)
            confi_files_ent.grid(row=4, column=1, sticky=tkinter.W)
            config_help = tkinter.Button(self.frm, text='?', command=lambda: help_message('configs_files'))
            config_help.grid(row=4, column=2, sticky="we")
            # Boton para ejecutar el llenado de archivos excel
            exec_assess_btn = tkinter.Button(self.frm, text='Llenar excel', command=self.llenar_excel_button)
            exec_assess_btn.grid(row=5, column=1, sticky="we")
            # Mensaje Estado
            state_lb = tkinter.Label(self.frm, textvariable=self.current_state)
            state_lb.grid(row=6, column=1)

    class GuiConfigurarSwitches:
        """
        Clase para configurar switches Meraki a partir de los assessment en excel
        """
        def __init__(self):
            self.frm = ''
            self.archivos_excel_str = ''
            self.seriales_sw_str = ''
            self.current_state = tkinter.StringVar()

        def config_sw_meraki(self):
            """
            Programa que corre al presionar el boton de configurar switches meraki
            """
            archivos_excel_conf = [archiv_str.strip() for archiv_str in self.archivos_excel_str.get().split(',')]
            seriales = [archiv_str.strip() for archiv_str in self.seriales_sw_str.get().split(',')]
            config_meraki_sw.config_sw_meraki(archivos_excel_conf, seriales, api_key_meraki)
            self.current_state.set("Process completed\n"
                                   "please verify the APs in the controller")

        def run_gui(self):
            """
            Ejecuta la interfaz gráfica para configurar los switches Meraki a partir de los assessments en excel
            """
            clear_work_area()
            self.frm = tkinter.Frame(master=root_win)
            self.frm.grid(row=0, column=0)
            self.frm.rowconfigure(0, weight=1, minsize=10)
            self.frm.rowconfigure(1, weight=1, minsize=10)
            self.frm.rowconfigure(2, weight=1, minsize=10)
            self.frm.rowconfigure(3, weight=1, minsize=10)
            self.frm.rowconfigure(4, weight=1, minsize=10)
            self.frm.columnconfigure(0, weight=1, minsize=10)
            self.frm.columnconfigure(1, weight=1, minsize=10)
            self.frm.columnconfigure(2, weight=1, minsize=10)
            # Titulo
            title_lb = ttk.Label(self.frm, text="Configurar SWs Meraki", anchor=tkinter.CENTER, font=('Helvetica', 12))
            title_lb.grid(row=0, columnspan=3, pady=10)
            # Ingresar listado de archivos de excel
            self.archivos_excel_str = tkinter.StringVar(self.frm)
            excel_files_lb = tkinter.Label(self.frm, text="Archivos excel de configuracion")
            excel_files_lb.grid(row=1, column=0, sticky=tkinter.W)
            excel_files_ent = tkinter.Entry(self.frm, textvariable=self.archivos_excel_str, width=50)
            excel_files_ent.grid(row=1, column=1, sticky=tkinter.W)
            excel_help = tkinter.Button(self.frm, text='?', command=lambda: help_message('excel_files_config'))
            excel_help.grid(row=1, column=2, sticky="we")
            # Ingresar listado de seriales
            self.seriales_sw_str = tkinter.StringVar(self.frm)
            seriales_sw_lb = tkinter.Label(self.frm, text="Seriales de switches")
            seriales_sw_lb.grid(row=2, column=0, sticky=tkinter.W)
            seriales_sw_ent = tkinter.Entry(self.frm, textvariable=self.seriales_sw_str, width=50)
            seriales_sw_ent.grid(row=2, column=1, sticky=tkinter.W)
            seriales_help = tkinter.Button(self.frm, text='?', command=lambda: help_message('seriales_sw'))
            seriales_help.grid(row=2, column=2, sticky="we")
            # Boton para configurar los switches meraki
            config_sw_btn = tkinter.Button(self.frm, text='Configurar switches Meraki', command=self.config_sw_meraki)
            config_sw_btn.grid(row=3, column=1, sticky="we")
            # Mensaje Estado
            state_lb = tkinter.Label(self.frm, textvariable=self.current_state)
            state_lb.grid(row=4, column=1)

    initial_win = tkinter.Frame(master=root_win)
    initial_win.grid(row=0, column=0, sticky="new")
    # Boton para extraer la informacion de las configuraciones
    gui_extract = GuiExtractConfig()
    btn_funcion1 = tkinter.Button(initial_win, text='Extraer configuraciones', command=gui_extract.run_gui)
    # Boton para configurar los switches Meraki
    gui_configure = GuiConfigurarSwitches()
    btn_funcion2 = tkinter.Button(initial_win, text='Configurar SWs Meraki', command=gui_configure.run_gui)

    btn_funcion1.grid(row=0, column=0)
    btn_funcion2.grid(row=1, column=0)


def main():
    window = tkinter.Tk()
    meraki_key = "138666754a71d2b90e40e763f83006175f593f86"
    exec_gui(window, meraki_key)
    window.mainloop()


if __name__ == '__main__':
    main()
