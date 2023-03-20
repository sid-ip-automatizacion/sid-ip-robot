import tkinter
import dotenv
import os
import keyring
from tkinter import ttk
from passlib.context import CryptContext
from pathlib import Path

import states
# import phase1
# TODO: adicionar la creacion de pantillas

class UserEnvironment:
    def __init__(self):
        self.passw =""  # Para verivicar el password de la aplicacion, no el de SCCD
        self.authenticated = False  # Indica si el usuariose autentico correctamente en la aplicacion
        self.attempts = 0  # Cantidad de intentos de autenticación en la aplicacion
        self.__hash_context = CryptContext(schemes=["pbkdf2_sha256"], default="pbkdf2_sha256",
                                                     pbkdf2_sha256__default_rounds=5000)  # Usado para hash del password
        self.__env_path = Path('.') / '.env'  # Ruta a las variables de ambiente
        dotenv.load_dotenv(dotenv_path=self.__env_path)

    def run_states(self):
        """
        Carga la ventana de cambios de estado
        """
        self.clear_work_area()  # Limpia el area de trabajo
        states.state_change(self)  # Ejecuta el cambio de estado en el ambiente del usuario

    # def run_templates(self):
    #     """
    #     Carga la ventana de plantillas
    #     """
    #     self.clear_work_area()  # Limpia el area de trabajo
    #     phase1.phase1_gui(self)  # Ejecuta el modulo de plantillas
    #TODO: Insertar la creación de plantillas

    def initial_work_area(self):
        """
        Carga la ventana inicial del area de trabajo
        """
        self.clear_work_area()  # Limpia el area de trabajo
        btn_submit = tkinter.Button(master=self.__work_area, text="Update States", height=2,
                               command=self.run_states)
        btn_submit.pack(pady=5)

        # btn_submit = tkinter.Button(master=self.__work_area, text="Plantillas", height=2,
        #                        command=self.run_templates)
        #TODO: Insertar creacion de plantillas
        btn_submit.pack(pady=5)
        self.__root.mainloop()

    def create_work_area(self):
        """
        Crea la ventana GUI donde se ejecutara el programa
        """
        self.__root = tkinter.Tk()  # Ventana principal
        self.__root.geometry("1100x600")
        self.__root.title('SID IP robot')
        # La siguiente seccion define un area de trabajo donde se ubicaran las ventanas de otras funciones
        def frame_configure(event):
            self.__my_canvas.config(width=event.width, height=event.height)
            self.__root.update_idletasks()
            self.__my_canvas.configure(scrollregion=self.__my_canvas.bbox(self.__windows_item))
        main_frame = tkinter.Frame(self.__root)
        main_frame.pack(fill=tkinter.BOTH, expand=True)
        main_frame.rowconfigure(0, weight=1, minsize=10)
        main_frame.rowconfigure(1, weight=1, minsize=5)
        main_frame.columnconfigure(0, weight=1, minsize=10)
        main_frame.columnconfigure(1, weight=1, minsize=5)
        self.__my_canvas = tkinter.Canvas(main_frame)
        scrollbar_vertical = ttk.Scrollbar(main_frame, orient='vertical', command=self.__my_canvas.yview)
        scrollbar_horizontal = ttk.Scrollbar(main_frame, orient='horizontal', command=self.__my_canvas.xview)
        self.__work_area = tkinter.Frame(master=self.__my_canvas, padx=10, pady=10)  # Area de trabajo
        self.__windows_item = self.__my_canvas.create_window((0, 0), window=self.__work_area, anchor="nw")
        main_frame.bind('<Configure>', frame_configure)
        self.__my_canvas.configure(yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)
        self.__my_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_horizontal.grid(row=1, column=0, sticky="ew", ipadx=10, ipady=10)
        scrollbar_vertical.grid(row=0, column=1, sticky="ns", ipadx=10, ipady=10)

        # Menu general
        menubar = tkinter.Menu(self.__root)
        self.__root.config(menu=menubar)
        filemenu = tkinter.Menu(menubar, tearoff=0)  # Menu Archivo
        filemenu.add_command(label="Minimize", command=lambda: self.__root.iconify())
        filemenu.add_separator()
        filemenu.add_command(label="Close", command=lambda: self.__root.destroy())
        myaccmenu = tkinter.Menu(menubar, tearoff=0)  # Menu Mi cuenta
        myaccmenu.add_command(label="Configure SCCD", command=self.set_sccd_credentials)
        myaccmenu.add_command(label="Change password", command=self.create_password)
        funmenu = tkinter.Menu(menubar, tearoff=0)  # Menu Funciones
        funmenu.add_command(label="Update States", command=self.run_states)
        #funmenu.add_command(label="Crear plantillas", command=self.run_templates)
        #TODO: Insertar creación de plantillas
        funmenu.add_separator()
        funmenu.add_command(label="Return to init", command=self.initial_work_area)
        infomenu = tkinter.Menu(menubar, tearoff=0)  # Menu Acerca de
        infomenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="File", menu=filemenu)  # Inserta menu Archivo
        menubar.add_cascade(label="My account", menu=myaccmenu)  # Inserta menu Mi cuenta
        menubar.add_cascade(label="Functions", menu=funmenu)  # Inserta menu Funciones
        menubar.add_cascade(label="Info", menu=infomenu)  # Inserta menu Funciones

    def adjust_window(self, window):
        """
        Aumenta el tamaño de un marco GUI al tamaño de la ventana
        :param window: Ventana que se quiere ajustar
        """
        if window.winfo_width() < self.__root.winfo_width():
            self.__root.update_idletasks()
            self.__my_canvas.itemconfig(self.__windows_item, width=self.__root.winfo_width())
            self.__my_canvas.configure(scrollregion=self.__my_canvas.bbox(self.__windows_item))
        if window.winfo_height() < self.__root.winfo_height():
            self.__root.update_idletasks()
            self.__my_canvas.itemconfig(self.__windows_item, height=self.__root.winfo_height())
            self.__my_canvas.configure(scrollregion=self.__my_canvas.bbox(self.__windows_item))

    def clear_work_area(self):
        """
        Limpia el area de trabajo
        """
        for widgets in self.__work_area.winfo_children():
            widgets.destroy()

    def create_password(self):
        """
        Cambia el password de acceso a la alicacion
        """
        def set_newpass():
            new_password = ent_newpass.get()
            if new_password == ent_confirm.get():
                hashed = self.__hash_context.hash(new_password)
                os.environ["SECRET_KEY_HASH"] = hashed
                dotenv.set_key(self.__env_path, 'SECRET_KEY_HASH', hashed)
                newpass_win.destroy()
            else:
                ent_newpass.delete(0, tkinter.END)
                ent_confirm.delete(0, tkinter.END)
                lbl_state.configure(text="Password not match")

        newpass_win = tkinter.Tk()
        newpass_msg = tkinter.Label(newpass_win, text="Enter new password")
        newpass_msg.grid(row=0, column=0, padx=10, pady=10)
        ent_newpass = tkinter.Entry(newpass_win, show="*", width=20)
        ent_newpass.grid(row=0, column=1, padx=10, pady=10)
        confirm_msg = tkinter.Label(newpass_win, text="Confirm password")
        confirm_msg.grid(row=1, column=0, padx=10, pady=10)
        ent_confirm = tkinter.Entry(newpass_win, show="*", width=20)
        ent_confirm.grid(row=1, column=1, padx=10, pady=10)
        btn_newpass = tkinter.Button(newpass_win, text="Change password", command=set_newpass)
        btn_newpass.grid(row=2, column=0, pady=5)
        lbl_state = tkinter.Label(newpass_win, text="")
        lbl_state.grid(row=3, column=0)
        newpass_win.mainloop()

    def auth_valid(self, passw):
        """
        Valida si una contraseña presentado es correcto
        :param passw: Contraseña a validar
        :return: Verdadero si la contraseña es correcta
        """
        hash_pass = os.environ["SECRET_KEY_HASH"]
        if self.__hash_context.verify(passw, hash_pass):
            return True
        else:
            return False

    def request_authent(self):
        """
        Solicita la autenticacón del usuario en una ventana grafica
        """

        def try_aut():
            if self.attempts < 5:
                self.passw = ent_password.get()
                self.authenticated = self.auth_valid(self.passw)
                if not self.authenticated:
                    self.attempts += 1
                    ent_password.delete(0, tkinter.END)
                    lbl_state.configure(text="Try again")
                else:
                    auth_win.destroy()
            else:
                lbl_state.configure(text="Too many tries")

        auth_win = tkinter.Tk()
        auth_win.title('SID-IP robot')
        auth_win.geometry("300x200")
        auth_msg = tkinter.Label(auth_win, text="Enter password")
        auth_msg.pack(pady=20)
        ent_password = tkinter.Entry(auth_win, show="*", width=20)
        ent_password.pack()
        btn_cont = tkinter.Button(auth_win, text="Continue", command=try_aut)
        btn_cont.pack(pady=20)
        lbl_state = tkinter.Label(auth_win, text="")
        lbl_state.pack()
        auth_win.mainloop()

    def set_sccd_credentials(self):
        """
        Guarda las credenciales de SCCD
        """
        def save_cred():
            user = ent_user.get()
            password = ent_pass.get()
            owner = ent_owner.get()
            os.environ["OWNER_SCCD"] = owner  # Guarda el usuario OWNER como variable de ambiente
            dotenv.set_key(self.__env_path, 'OWNER_SCCD', owner)  # Almacena usuario OWNER en archivo .env
            os.environ["LOGIN_USER_SCCD"] = user  # Guarda el usuario de login como variable de ambiente
            dotenv.set_key(self.__env_path, 'LOGIN_USER_SCCD', user)  # Almacena usuario de login en archivo .env
            keyring.set_password("SCCD_KEY", user, password)  # Guarda el password en el banco de contraseñas del sistema operativo
            sccd_cred_win.destroy()

        sccd_cred_win = tkinter.Tk()
        user_msg = tkinter.Label(sccd_cred_win, text="Login User SCCD")
        user_msg.grid(row=0, column=0, padx=10, pady=10)
        ent_user = tkinter.Entry(sccd_cred_win, width=20)
        ent_user.grid(row=0, column=1, padx=10, pady=10)
        pass_msg = tkinter.Label(sccd_cred_win, text="Password SCCD")
        pass_msg.grid(row=1, column=0, padx=10, pady=10)
        ent_pass = tkinter.Entry(sccd_cred_win, show="*", width=20)
        ent_pass.grid(row=1, column=1, padx=10, pady=10)
        owner_msg = tkinter.Label(sccd_cred_win, text="Owner Person SCCD")
        owner_msg.grid(row=2, column=0, padx=10, pady=10)
        ent_owner = tkinter.Entry(sccd_cred_win, width=20)
        ent_owner.insert(tkinter.END, ent_user.get())
        ent_owner.grid(row=2, column=1, padx=10, pady=10)
        btn_save = tkinter.Button(sccd_cred_win, text="Save Credentials", command=save_cred)
        btn_save.grid(row=3, column=0, pady=5)
        sccd_cred_win.mainloop()

    def get_root_window(self):
        return self.__root

    def get_work_area(self):
        return self.__work_area

    def get_user_sccd(self):
        """
        Obtiene el usuario de SCCD desde las variables de entorno
        :return: Usuario de SCCD
        """
        return os.environ["LOGIN_USER_SCCD"]

    def get_pass_sccd(self):
        """
        Obtiene la contraseña de SCCD desde el banco de contraseñas del sistema operativo
        :return: Contraseña de SCCD
        """
        return keyring.get_password("SCCD_KEY", self.get_user_sccd())
    def get_owner_sccd(self):
        """
        Obtiene el owner de SCCD desde las variables de entorno
        :return: Owner de SCCD
        """
        return os.environ["OWNER_SCCD"]

    def get_urlsccd(self):
        """
        Obtiene la url de sccd
        :return: URL para los request a SCCD
        """
        return os.environ["SCCD_URL"]

    def show_about(self):
        """
        Muestra la ventana Acerca de"
        """
        about_win = tkinter.Tk()
        about_text = tkinter.Label(about_win, text='version: 1.2'
                                                  '\n\nDesarrollado por SID-IP Team, Cable & Wireless'
                                                  '\nEquipo de desarrollo:'
                                                  '\nAlvaro Molano, Cesar Castillo, Jose Cabezas, Nicole Paz, Ricardo Gamboa, William Galindo')
        about_text.pack()
        about_win.mainloop()
