import re

'''
Este modulo permite identificar unas variables que siguen el formato dado por una plantilla, en donde se reemplaza el
texto de la variable por la clave #VAR_n, siendo n el número de identificación de la variable
El módulo permite extraer bloques de un archivo de texto que contiene la configuración del dispositivo e identifica y
extrae las variables de cada bloque de texto
Finalmente se obtiene un array de diccionarios, en el que cada diccionario contiene las variable encontradas en cada
bloque de texto
'''

def extract_blocks(file, start_with, end_with):
    """
    Extrae bloques de texto de un archivo con la configuración original y los almacena en un array
    :param file: Archivo de texto con configuracion original del cual se van a extraer los bloques
    :param start_with: Expresión con la que empieza la línea que identifica el inicio del bloque de texto
    :param end_with: Expresión con la que empieza la línea que identifica el fin del bloque
    :return: Array en el que cada elemento es un bloque de texto, y cada bloque de texto es a su vez una lista donde
    cada línea de texto es un elemento de la lista
    """
    array_blocks = []
    with open(file) as original_file:
        writing_block = False
        for linea in original_file:
            if not writing_block:
                if linea.startswith(start_with):
                    writing_block = True
                    interface_original = [linea.strip()]
            elif linea.startswith(end_with):
                writing_block = False
                array_blocks.append(interface_original)
            else:
                interface_original.append(linea.strip())
    return array_blocks


def buscar_variables(linea_busqueda, num_var, curr_var, plantilla):
    """
    Dada una linea de texto busca las variables definidas en la plantilla que se encuentran en esa línea y las devuelve
    en un diccionario
    :param linea_busqueda: Linea de texto donde se buscan las variables
    :param num_var: Cantidad de variables definidas en la plantilla
    :param curr_var: Diccionario con las variables que ya se han encontrado en una búsqueda anterior
    :param plantilla: Archivo de texto donde está definida la plantilla con las variables
    :return: Diccionario con las variables encontradas, la llave que identifica cada variable tiene el formato VAR_<numero>
    """
    with open(plantilla) as plantilla_file:
        for linea_plantilla in plantilla_file:
            patron = linea_plantilla.strip()
            for var_bus in range(1, num_var+1):
                variable = '#VAR_{}'.format(var_bus)
                exp_regular = '(?P<VAR_{}>[^\s]+)'.format(var_bus)
                if variable in patron:
                    patron = re.sub(variable, lambda x: exp_regular, patron)+'$'
            encontrados = re.search(patron, linea_busqueda)
            if encontrados:
                for var_enc in range(1, num_var+1):
                    try:
                        curr_var['VAR_{}'.format(var_enc)] = encontrados.group('VAR_{}'.format(var_enc))
                    except:
                        continue
    return curr_var


def get_array_variables(config_file, cantidad_variables, plantilla):
    """
    Extrae los bloques de texto deseados y encuentra las variables en cada bloque
    :param config_file: Archivo de texto con la configuración original de donde se extraerá el texto
    :param cantidad_variables: Cantidad de variables definidas en la plantilla
    :param plantilla: Archivo de texto donde se define la plantilla
    :param start_with: Expresión para encontrar la línea que inicia el bloque que se busca
    :param end_with: Expresión para encontrar la línea que finaliza el bloque que se busca
    :return: Array en el que cada elemento es un diccionario con las variables encontradas dentro del bloque de texto
    """
    with open(plantilla) as plantilla_file:
        for linea_plantilla in plantilla_file:
            if 'inicio_bloque_interface:' in linea_plantilla:
                start_with = linea_plantilla.partition('inicio_bloque_interface:')[2].strip()
            elif 'fin_bloque_interface:' in linea_plantilla:
                end_with = linea_plantilla.partition('fin_bloque_interface:')[2].strip()
            else:
                continue
    bloques = extract_blocks(config_file, start_with, end_with)
    print(bloques)
    array_variables = []
    for bloque_actual in bloques:
        variables = {}
        for linea_actual in bloque_actual:
            variables = buscar_variables(linea_actual, cantidad_variables, variables, plantilla)
        array_variables.append(variables)
    return array_variables


def main():

    print("funcion main")
    # valores_variables = get_array_variables(config_file='ejemplo-configuracion.txt', cantidad_variables=5,
    #                                         plantilla='plantilla1.cfg', start_with='interface Gi', end_with='!

    # for imprimir in valores_variables:
    #     print(imprimir)

if __name__ == "__main__":
    main()
