import meraki
import json
import time
import openpyxl
from pathlib import Path

"""
Este modulo configura automaticamente los switches meraki a partir de los assessment en excel
"""

class SwitchPortMeraki:
    def __init__(self):
        self.sw_serial = None
        self.port_number = None
        self.port_name = ''
        self.mode = 'access'
        self.vlan = 1
        self.tagvlans = 'all'
        self.voicevlan = None
        self.stp_guard = 'disabled'
        self.poe = True
    def update_port(self, dashboardmeraki):
        try:
            config_response = dashboardmeraki.switch.updateDeviceSwitchPort(self.sw_serial, self.port_number, name=self.port_name,
                                                                            type=self.mode, vlan=self.vlan, allowedVlans=self.tagvlans,
                                                                            voiceVlan=self.voicevlan, stpGuard=self.stp_guard,
                                                                            poeEnabled=self.poe)
            print(config_response)
        except meraki.exceptions.APIError as err:
            print('Problema al configurar puerto {} del switch {}'.format(self.port_number, self.sw_serial))
            print(err)

def create_switches(excel_files, seriales):
    """
    Crea un array en el que cada elemento de la lista es un switch y cada switch contiene una lista con los puertos del
    switch. Cada puerto es un objeto de la clase SwitchPortMeraki
    :param excel_files: listado de archivos de exckl con configuración de siwtches
    :param seriales: listado de seriales de los switches
    :return: lista donde cada elemento de primer nivel representa un switch y cada elemento de segundo nivel es otra lista
    con objetos de la clase SwitchPortMeraki que representan los puertos del switch
    """
    switches = []
    for serial, excel in zip(seriales, excel_files):
        switch_assess = Path.cwd().joinpath('assessments', excel)
        sw_wb = openpyxl.load_workbook(switch_assess)
        sw_sh = sw_wb['SW']
        switch_ports = []
        for sw_row in sw_sh.iter_rows(min_row=2):
            if sw_row[0].value != None:
                sw_port = SwitchPortMeraki()
                sw_port.sw_serial = serial
                sw_port.port_number = sw_row[0].value.strip()
                sw_port.mode = 'access' if sw_row[1].value is None else sw_row[1].value.strip()
                sw_port.port_name = '' if sw_row[2].value is None else sw_row[2].value.strip()
                sw_port.vlan = 1 if sw_row[3].value is None else int(sw_row[3].value.strip())
                sw_port.tagvlans = 'all' if sw_row[4].value is None else sw_row[4].value.strip()
                sw_port.voicevlan = None if sw_row[5].value is None else int(sw_row[5].value.strip())
                sw_port.stp_guard = 'disabled' if sw_row[6].value is None else sw_row[6].value.strip()
                if sw_row[7].value is None:
                    sw_port.poe = True
                elif sw_row[7].value.lower() == 'false':
                    sw_port.poe = False
                else:
                    print(sw_row[7].value.lower())
                    sw_port.poe = True
                switch_ports.append(sw_port)
        switches.append(switch_ports)
    return switches

def config_sw_meraki(excel_paths, seriales_sws, api_key):
    """
    Funcion para ejecutar el modulo de configuracion de switches desde otro modulo externo
    """
    dashboard = meraki.DashboardAPI(api_key, suppress_logging=True)  # crear dasboard de la libreria meraki
    lista_switches = create_switches(excel_paths, seriales_sws)  # genera una lista con la información de puertos de los switches

    for index, switch in enumerate(lista_switches):  # configura los puertos para todos los switches
        print("inicia configuracion de switch {}".format(index))
        for puerto in switch:
            print("Configura puerto {} en switch {}".format(puerto.port_number, puerto.sw_serial))
            time.sleep(0.25)
            puerto.update_port(dashboard)




def main():
    config_file_path = Path.cwd().joinpath('config_meraki_info1.cfg')  # leer variables de configuracion
    with open(config_file_path) as file:
        config_values = json.load(file)
        API_KEY = config_values['API_KEY_MERAKI']
        excel_paths = config_values['Assessments_Excel']
        seriales_sws = config_values['Seriales_switches']

    dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)  # crear dasboard de la libreria meraki

    lista_switches = create_switches(excel_paths, seriales_sws) # genera una lista con la información de puertos de los switches

    for index, switch in enumerate(lista_switches):  #configura los puertos para todos los switches
        print("inicia configuracion de switch {}".format(index))
        for puerto in switch:
            print("Configura puerto {} en switch {}".format(puerto.port_number, puerto.sw_serial))
            time.sleep(0.25)
            puerto.update_port(dashboard)

if __name__ == '__main__':
    main()