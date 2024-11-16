import tkinter
from tkinter.filedialog import asksaveasfilename
import meraki
import pandas as pd


from .atpSWinfo_data import MerakiSWinfo as Minfo
from .select_client import main as select

"""
Este módulo muestra y maneja la ventana  de ATP SW 
"""


def error_window(text):
        #ventana de error
        print("ERROR: {}".format(text))
        error_win = tkinter.Tk()
        error_text = tkinter.Label(error_win, text=text)
        ok_button = tkinter.Button(error_win, text='OK', width=5, height=2, command=error_win.destroy)
        error_text.pack()
        ok_button.pack()
        error_win.mainloop()


def get_org(API_KEY):
    # Se obtiene la información de todas las organizaciones
    #  
    responseOK = False
    tries_counter = 0
    orgs = None

    dashboard = meraki.DashboardAPI(API_KEY, output_log=False, print_console=False)
    while responseOK == False :
        """
        La solicitud de la información de las organización salta error de forma aleatoria (cosas de Meraki)
        Este While maneja las excepciones y vuelve a intentarlo hasta 10 veces
        """
        try:
            orgs = dashboard.organizations.getOrganizations()
            print(":::RESPONSE:::")
            #print(response)
            responseOK = True
            return orgs
        except :
            print("hubo un error")
            tries_counter + 1
            pass
        if tries_counter > 10:
            responseOK = True
            print("No authorization")
            error_window('No ORG authorization')
            return



def main_select_client(api_key):
    clients = []
    array_orgs =get_org(api_key) # obtiene todas las org info
    #Se realiza filtrado para tener únicamente el name y el id de la organización
    for count, organization in enumerate(array_orgs):
        clientinfo = (organization['name'], organization['id'])
        clients.append(clientinfo)
        print('{}. {} has id: {}'.format(count, organization['name'], organization['id']))
    clients.sort()
    # una vez obtenida todas las org en formato [(name,orgid)...] se pasan a la función main  del módulo select_client para abrir la ventana de selección
    client = select(clients)
    # se retorna el OrgID de la Organizacíon seleccionada
    return client



def save_excel(datos):

    """
    Esta función recibe cualquier arreglo en formato Diccionary y genera un archivo excel para guardado
    """

    # Crear el DataFrame
    df = pd.DataFrame(datos)
    
    # Cuadro de diálogo para guardar archivo
    file_path = asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        title="Guardar como"
    )

    if file_path:
        # Guardar el DataFrame en Excel
        df.to_excel(file_path, index=False)
        print(f"Archivo guardado en: {file_path}")
    else:
        print("Guardado cancelado.")

def get_atp_button_function(meraki_key_api):
    # Funcipón principal del botón 'Get ATP SW Meraki'
    org_id = main_select_client(meraki_key_api) #Se solicita selección de Organización, se retorna el ID de la Org
    switches=Minfo() # Se instancia objeto para obtener info de sw
    dic_swinfo = switches.get(meraki_key_api,org_id) # Se ejecuta método que solicita el org_id y devuelve toda la info de los SW en formato Dictionary
    if dic_swinfo == None:
        error_window("No hay acceso a esta organización, verificar configruación se seguridad")
    else: 
        save_excel(dic_swinfo) # Se guarda la información de los SW en formato Excel

    


def main_function(root_win, meraki_key_api):

    # Esta función mostrará el botón y  lo asociará la secuencia funcional requerida 

    initial_win = tkinter.Frame(master=root_win)
    initial_win.grid(row=0, column=0, sticky="new")
    # Botón para obtener ATP de los APs
    btn_funcion1 = tkinter.Button(initial_win, text='Get ATP SW Meraki', command= lambda: get_atp_button_function(meraki_key_api))
    btn_funcion1.grid(row=0, column=0)
