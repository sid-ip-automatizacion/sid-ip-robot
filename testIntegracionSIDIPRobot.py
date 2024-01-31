import tkinter
from tkinter import ttk
import GUIconfigsw  # importar el modulo

"""
El programa a integrar debe tener una función o metodo que acepte como primera entrada una ventana de tkinter, la cual
se usará como su ventana root, en la que se graficara toda la función. Opcionalmente puede acpetar como entradas variables
que se tomarán del entorno general del usuario, normalemente variable que quiera mantener almacenadas permanentemente en
el computador como nombres de usuario, passwords y urls
"""
########################################################################################################################
# En la siguiente linea defina modulo_run_function como la función o el método que ejecuta el modulo a probar
modulo_run_function = GUIconfigsw.exec_gui

# En la siguiente sección llene los valores de las variables que use en la función a probar, los parametros que no
# use dejelos con valor None
user1 = None
user2 = None
password1 = "138666754a71d2b90e40e763f83006175f593f86"
password2 = None
url1 = None
url2 = None
###########

# En la siguiente linea incluya en la lista los nombres de prueba de los argumentos que se pasan a la función, Recuerde
# que el primer valor siempre debe ser la ventana de tkainter que se usara como root para graficar la función a probar:
lista_argumentos = ['root_win', 'password1']
########################################################################################################################


class UserEnvironment:
    """
    La clase UserEnvironment contiene los atributos y metodos que permiten crear la interfaz gráfica que comparten las
    distintas funcionalidades
    """
    def __init__(self, user1, user2, password1, password2, url1, url2):
        """
        Constructor de la clase, establece los parametros iniciales
        :param user1: Usuario de prueba 1
        :param user2: Usuario de prueba 2
        :param password1: Clave de prueba 1
        :param password2: Clave de prueba 2
        :param url1: URL de prueba 1
        :param url2: URL de prueba 2
        """
        if user1:
            self.user1 = user1
        if user2:
            self.user2 = user2
        if password1:
            self.password1 = password1
        if password2:
            self.password2 = password2
        if url1:
            self.url1 = url1
        if url2:
            self.url2 = url2
        self.testing_arguments = []


    def run_fuction(self):
        """
        Carga la ventana de cambios de la funcion
        """
        self.clear_work_area()  # Limpia el area de trabajo
        modulo_run_function(self.get_work_area(), *self.testing_arguments)  # Ejecuta la funcion en el ambiente del usuario

    def initial_work_area(self):
        """
        Carga la ventana inicial del area de trabajo
        """
        self.clear_work_area()  # Limpia el area de trabajo
        # Boton de Ejecutar Funcion
        btn_submit = tkinter.Button(master=self.get_work_area(), text="Ejecutar funcion", height=2,
                                    command=self.run_fuction)
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
        def working_area_configure(event):
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
        self.__my_canvas.configure(scrollregion=self.__my_canvas.bbox(self.__windows_item))
        self.__work_area.bind('<Configure>', working_area_configure)

        # Menu general
        menubar = tkinter.Menu(self.__root)
        self.__root.config(menu=menubar)
        funmenu = tkinter.Menu(menubar, tearoff=0)  # Menu Funciones
        funmenu.add_command(label="Ejecutar funcion", command=self.run_fuction)
        menubar.add_cascade(label="Functions", menu=funmenu)  # Inserta menu Funciones

    def clear_work_area(self):
        """
        Limpia el area de trabajo
        """
        for widgets in self.__work_area.winfo_children():
            widgets.destroy()

    def get_work_area(self):
        return self.__work_area

    def set_testing_arguments(self, arg_list):
        self.testing_arguments = arg_list

    def get_user1(self):
        return self.user1

    def get_user2(self):
        return self.user2

    def get_password1(self):
        return self.password1

    def get_password2(self):
        return self.password2

    def get_url1(self):
        return self.url1

    def get_url2(self):
        return self.url2


def main():
    gui_env = UserEnvironment(user1, user2, password1, password2, url1, url2)
    arg_final = [None]*len(lista_argumentos)
    for index, argument in enumerate(lista_argumentos):
        if index == 0 and argument != 'root_win':
            print("ERROR, recuerde que el primer argumento siempre debe ser el root_win")
            break
        elif argument == 'root_win':
            pass
        elif argument == 'user1':
            arg_final[index] = gui_env.get_user1()
        elif argument == 'user2':
            arg_final[index] = gui_env.get_user2()
        elif argument == 'password1':
            arg_final[index] = gui_env.get_password1()
        elif argument == 'password2':
            arg_final[index] = gui_env.get_password2()
        elif argument == 'url1':
            arg_final[index] = gui_env.get_url1()
        elif argument == 'url1':
            arg_final[index] = gui_env.get_url2()
        else:
            print("No se encotro el argumento. Recuerde los posibles argumentos:")
            print("root_win, user1, user2, password1, password2, url1, url2")
    arg_final.pop(0)
    print("Valores que se pasaran como argumentos:",'root_win', *arg_final)
    gui_env.create_work_area()
    gui_env.set_testing_arguments(arg_final)
    gui_env.initial_work_area()










if __name__ == "__main__":
    main()
