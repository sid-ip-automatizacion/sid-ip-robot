import openpyxl
import json
from pathlib import Path

import find_variables

"""
Este modulo permite llenar de manera automatica los archivos de excel con los assessment de LAN
"""

class WriteExcell:
    """
    Escribe la plantilla en Excel
    """

    def __init__(self, file):
        self.file_path = file

    def write_assessment(self, interfaces_info):
        sw_assessment_wb = openpyxl.Workbook()
        sw_assessment_sh = sw_assessment_wb.active
        sw_assessment_sh['A1'] = "Port"
        sw_assessment_sh['B1'] = "Port mode"
        sw_assessment_sh['C1'] = "Description"
        sw_assessment_sh['D1'] = "Native vlan"
        sw_assessment_sh['E1'] = "Tag vlans"
        sw_assessment_sh['F1'] = "Voice vlan"
        sw_assessment_sh['G1'] = "STP guard"
        sw_assessment_sh['H1'] = "PoE(True/False)"
        for interf in interfaces_info:
            sw_assessment_sh.append(interf)
        sw_assessment_sh.title = 'SW'
        try:
            sw_assessment_wb.save(self.file_path)
            print('Archivo ' + str(self.file_path) + ' salvado')
        except:
            print('Falla en salvar archivo ' + str(self.file_path))


def convert_var_dict_to_list(match_var_field, val_interfaces):
    """
    Transforma las variables definidas en un dicionario con keys VAR_n en la lista de columnas a escribir en excel
    :param match_var_field: Diccionario donde se relaciona el valor VAR_n con la variable a escribir
    :param val_interfaces: Diccionario con los valores con keys VAR_n
    :return: lista con valores de las interfaces a escribir en excel
    """
    interf_values = []
    for curr_int in val_interfaces:
        int_val = [curr_int.get(match_var_field.get("port")), curr_int.get(match_var_field.get("port_mode")),
                   curr_int.get(match_var_field.get("description")), curr_int.get(match_var_field.get("native_vlan")),
                   curr_int.get(match_var_field.get("tag_vlans")), curr_int.get(match_var_field.get("voice_vlan")),
                   curr_int.get(match_var_field.get("stp_guard")), curr_int.get(match_var_field.get("poe"))]
        interf_values.append(int_val)

    return interf_values


def get_interface_values(config_file_path, config_sw_path, plantilla_name):
    """
    Lee el archivo original y genera la lista de valores que se escribiran en el archivo excel
    :param config_file_path: archivo de configuracion del modulo
    :param config_sw_path: direccion de archivo con configuración original del switch
    :return: lista de valores de interfaces a escribir en el excel
    """
    with open(config_file_path) as con_file:
        config_values = json.load(con_file)
        variable_field_match = config_values['variable_names']
        plantilla_path = Path.cwd().joinpath('sw_model_templates', plantilla_name)
        valores_interfaces = find_variables.get_array_variables(config_file=config_sw_path, cantidad_variables=10,
                                                                plantilla=plantilla_path)
        interfaces_config = convert_var_dict_to_list(variable_field_match, valores_interfaces)
    return interfaces_config


def execute_assess(excel_assess, original_configs, plantilla, variable_map):
    """
    Función para ejecutar el modulo desde otro modulo externo
    """

    config_file_path = Path.cwd().joinpath('var_mapings', variable_map)

    escritor = WriteExcell('')
    for (assess, original) in zip(excel_assess, original_configs):
        escritor.file_path = Path.cwd().joinpath('assessments', assess)
        origin_sw_config = Path.cwd().joinpath('switch_config_files', original)
        port_values = get_interface_values(config_file_path, origin_sw_config, plantilla)
        escritor.write_assessment(port_values)

def main():

    config_file_path = Path.cwd().joinpath('write_excel_config_test.cfg')

    with open(config_file_path) as file:
        total_values = json.load(file)
        excel_files_main = total_values['archivos_assessment_excel']
        original_configs_main = total_values['archivos_configuracion_original']

    escritor = WriteExcell('')
    for (assess, original) in zip(excel_files_main, original_configs_main):
        escritor.file_path = Path.cwd().joinpath('assessments', assess)
        origin_sw_config = Path.cwd().joinpath('switch_config_files', original)
        port_values = get_interface_values(config_file_path, origin_sw_config)
        escritor.write_assessment(port_values)


if __name__ == '__main__':
    main()
