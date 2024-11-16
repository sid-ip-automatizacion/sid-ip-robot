import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any


class Timer:
    def __init__(self):
        
        """
        Función contructora de contrador
        Inicialización de todos los valores del contador en 0
        Inicialización de las vanderas utilizadas para detener en contador y reiniciarlo
        El objeto gestiona una variable StringVar()  de tkinter que es consumida en el módulo de states

        """

        self.hrs = self.mins = self.secs = 0 #horas, minutos y segundos
        self.secs_rest = 0
        self.time_left = "00:00:00" # tiempo 0
        self.stop_flag = False # Se utiliza para declarar pausa
        self.finish_flag = False # Se utiliza para a declarar finalización
        self.thread_running = False # Se utiliza para rastrear si el hilo está en ejecución

        #Inicialización del StringVar que tendrá el valor del tiempo restante.
        # Esta variable será consumida para visualizar el tiempo restante
        self.tk_time = tk.StringVar() 
        self.tk_time.set(self.time_left)

        self.counter_thread = None # Se inicializa como None para manejar el primer caso de conteo
 

    #Se define la función de contador 
    def count(self, hrs_entd, min_entd, sec_entd=0):
        if self.thread_running:
            #Este codicional corre finish() para garantizar que muera el count() que está corriendo sobre el hilo anterior.
            self.finish()
            self.counter_thread.join()
            self.thread_running=False
        def run_counter():
            self.thread_running = True
            self.secs_rest = hrs_entd * 3600 + min_entd * 60 + sec_entd
            if self.finish_flag == True:
                self.stop_flag = False
                self.finish_flag = False
            while self.secs_rest and not self.stop_flag:
                self.hrs, remain_h = divmod(self.secs_rest, 3600)
                self.mins, self.secs = divmod(remain_h, 60)
                self.time_left = f'{self.hrs:02d}:{self.mins:02d}:{self.secs:02d}'
                self.tk_time.set(self.time_left)
                time.sleep(1)
                self.secs_rest -= 1
            print("Contador detenido." if self.stop_flag else "¡Tiempo Finalizado!")
        #La función interna del contador se define en un thread para que corra paralelo con el  resto del código
        if self.thread_running == False:
            self.counter_thread = threading.Thread(target=run_counter)
            self.counter_thread.start()
            print("nuevo hilo")
            
            

    def stop(self):
        #Método para pausar el contador
        self.stop_flag = True

    def contin(self):
        #Método para continuar el contador
        self.stop_flag = False
        hr, mn, sc = self.time_left.split(":")
        self.count(int(hr),int(mn),int(sc))
        
    def finish(self):
        #Método para terminar y reiniciar el contador a 00:00:00
        self.finish_flag = True
        self.stop_flag = True
        self.hrs = self.mins = self.secs = self.secs_rest = 0
        self.time_left = "00:00:00"
        self.tk_time.set(self.time_left)





""""
Se intentó crear una clase generadora de Timer() pero se pierde herencia en el proceso
No se descarta probarlo de otra forma

class Multi_Timer:
    #Generador de múltiples objetos Timer()
    def __init__(self):
        self.elements={}

    def generate(self,WO_label_list: Dict[str, Any]):
        print('debug_generate: ',WO_label_list)
        for WO, label in WO_label_list.items():
            self.elements[WO]=Timer(label)
"""

elements={}

#Función generadora, recibe la lista de WO y devuelve un dicionario con el formato {WO:objeto contador}
def generate(WO_list: List[str]):
    
    for WO in WO_list:
        if WO in elements:
            elements[WO].finish()
            elements[WO]=Timer()
        else:
            elements[WO]=Timer()
    return elements





