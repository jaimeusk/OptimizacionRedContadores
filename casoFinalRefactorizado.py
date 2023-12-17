# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 11:07:33 2023

Caso Final. Refactorizado

@author: jaime
"""


import pandas as pd
from ortools.linear_solver import pywraplp
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from tabulate import tabulate
import math
import time

from imprimeGraficos import pintar_dispositivos, pintar_dispositivos_en_rango

tiempoInicio = time.time()
print("\nInicio ejecución\n")
plt.close('All')



#%% Definición de funciones utiles para el programa

def dispositivos_en_rango_lista(nodos, dispositivos, distancia_maxima=0):
    '''
    Devuelve todos los dispositivos candidatos a conectarse con cada uno de los
    nodos de una lista.
    Por ejemplo, devuelve todos los routers candidatos a conectarse con cada
    uno de los routers del escenario.

    Argumentos:
    - nodos (list): Lista de nodos con coordenadas (nombre, x, y).
    - dispositivos (list(list)): Lista de dispositivos con coordenadas (nombre, x, y).
    - distancia_maxima (float): (Opcional para terminales) Distancia máxima para considerar dispositivos cercanos.

    Devuelve:
    - list: Lista de listas de dispositivos dentro del rango especificado alrededor de cada nodo.
    '''
     
    dispositivos_cercanos_por_nodo = []

    for nodo in nodos:
        # Si no pasamos un valor de distancia_maxima, usamos la distancia max
        # almacenada en el valor de cada nodo (Solo vale para terminales)
        if len(nodo) > 3:
            distancia_maxima = nodo[3]
            
        x_nodo, y_nodo = nodo[1], nodo[2]
        dispositivos_cercanos = {"Referencia":nodo, "Vecinos":[]}
        
        for dispositivo in dispositivos:
            x_dispositivo, y_dispositivo = dispositivo[1], dispositivo[2]
            distancia = math.sqrt((x_dispositivo - x_nodo)**2 + 
                                  (y_dispositivo - y_nodo)**2)
            if distancia <= distancia_maxima:
                dispositivos_cercanos["Vecinos"].append(dispositivo)

        dispositivos_cercanos_por_nodo.append(dispositivos_cercanos)

    return dispositivos_cercanos_por_nodo


def dispositivos_en_rango(nodo, dispositivos, distancia_maxima):
    '''
    Encuentra los dispositivos cercanos a un nodo dentro de una distancia máxima.

    Argumentos:
    - nodo (list): Coordenadas (nombre, x, y) del nodo central.
    - dispositivos (list(list)): Lista de dispositivos con coordenadas (nombre, x, y).
    - distancia_maxima (float): Distancia máxima para considerar dispositivos cercanos.

    Devuelve:
    - list: Lista de dispositivos dentro del rango especificado alrededor del nodo.
    '''
    
    x_nodo, y_nodo = nodo[1], nodo[2]
    dispositivos_cercanos = []

    for dispositivo in dispositivos:
        x_dispositivo, y_dispositivo = dispositivo[1], dispositivo[2]
        distancia = math.sqrt((x_dispositivo - x_nodo)**2 + 
                              (y_dispositivo - y_nodo)**2)
        if distancia <= distancia_maxima:
            dispositivos_cercanos.append(dispositivo)

    return dispositivos_cercanos

def leerDatos (hoja,x1, y1, x2, y2, orientacion):
    '''
    Lee datos de un archivo Excel en función dadas unas coordenadas y 
    una orientación de lectura.

    Argumentos:
    - x1 (int): Coordenada x inicial.
    - y1 (int): Coordenada y inicial.
    - x2 (int): Coordenada x final.
    - y2 (int): Coordenada y final.
    - orientacion (int): Orientación de extracción (0 para columnas, 1 para filas).

    Devuelve:
    - list: Lista con los datos extraídos del archivo Excel.
    '''
    
    x1=x1-1
    x2=x2-1
    y1=y1-1
    y2=y2-1
    df = pd.read_excel('Caso_HLP_2023.xlsx',sheet_name=hoja,header=None)
    i = 0
    l=[]
    if orientacion == 1:
        while (i+y1 <=y2):
            l.append(list(df.iloc[y1+i][x1:x2+1]))
            i=i+1
    if orientacion == 0:
        while (i+x1 <=x2):
            l.append(list(df[x1+i][y1:y2+1]))
            i=i+1
    return l


        

def pintar_nodo_rango(nodo, distanciaMax):
    """
    Función para pintar un nodo con un círculo que representa su rango máximo.

    Parametros:
        - nodoe (list): Lista que contiene las coordenadas x, y y el nombre del nodo.
        - distanciaMax (float): Valor que representa la distancia máxima del rango.

    Devuelve:
        Nada
    """
    
    x, y = nodo[1], nodo[2]
    nombre = nodo[0]
    plt.scatter(x, y, color='red', marker='*')
    plt.text(x, y, nombre, fontsize=10, ha='right')


    # Dibujar el círculo alrededor del terminal
    circulo = plt.Circle((x, y), distanciaMax, edgecolor='red', 
                         facecolor='blue',alpha=0.3)
    plt.gcf().gca().add_artist(circulo)
    

def imprimir_tabla_cortada(datos,letra):
    """
    Imprime una tabla procesada a partir de los datos dados, mostrando como máximo 3 columnas por fila.
    Si hay más de 3 columnas de datos por fila, se muestra '...' para indicar la limitación.
    
    Parámetros:
        - datos: Lista de datos para procesar y mostrar en la tabla.
        - letra: Carácter o cadena para etiquetar las columnas en la tabla.
    
    Devuelve:
        -nada
    """
    
    datos_procesados = []
    i = 0
    for fila in datos:
        if len(fila) > 3:
            fila = fila[:3] + ["..."]
        datos_procesados.append(fila)
        if i >= 5:
            datos_procesados.append(["..."] * len(fila))
            break
        i += 1
        
    
    l = str(letra)
    headers = [l+"[t][0]", l+"[t][1]", l+"[t][2]", l+"[t][.]"]
    print(tabulate(datos_procesados, headers=headers, tablefmt="grid"))
    print("\n")


           
 
def dibujar_nodos_con_texto(posiciones):
    """
    Dibuja los nodos en un gráfico con texto asociado a cada nodo.

    Parámetros:
        - posiciones (dict): Diccionario con las posiciones de los nodos activos

    Dibuja los nodos en un gráfico, asignando distintos marcadores y colores según su tipo:
        - Terminales (T): marcador '*', color rojo, tamaño 50.
        - Routers (R):
            - Routers WPAN: marcador 's', color morado, tamaño 200.
            - Routers GPRS: marcador 's', color verde, tamaño 200.
        - Concentradores (C): marcador 'o', color azul, tamaño 400.
    Agrega texto a cada nodo para identificarlo en el gráfico.
    """
    for nodo, (x, y) in posiciones.items():
        if nodo.startswith('T'):
            plt.scatter(x, y, marker='*', color='salmon', s=50, label=nodo)
            plt.text(x, y, nodo, ha='right', va='bottom', fontsize=8, color='black')
        elif nodo.startswith('R'):
            if nodo.endswith('W'):
                plt.scatter(x, y, marker='s', color='plum', s=200, label=nodo)
                plt.text(x, y, nodo, ha='right', va='bottom', fontsize=8, color='black')
            elif nodo.endswith('G'):
                plt.scatter(x, y, marker='s', color='LightGreen', s=200, label=nodo)
                plt.text(x, y, nodo, ha='right', va='bottom', fontsize=8, color='black')
        elif nodo.startswith('C'):
            plt.scatter(x, y, marker='o', color='skyblue', s=400, label=nodo) 
            plt.text(x, y, nodo, ha='right', va='bottom', fontsize=8, color='black')
        
 
    
def dibujar_conexiones(conexiones, posiciones, color, estilo):
    """
    Dibuja las conexiones entre dispositivos en un gráfico.

    Parámetros:
        - conexiones (dict): Diccionario que contiene las conexiones y sus valores.
        - posiciones (dict): Diccionario con las posiciones de los dispositivos.
        - color (str): Color de las flechas que representan las conexiones.
        - estilo (str): Estilo de línea de las flechas (p. ej., 'solid', 'dashed', 'dotted').
    
    Devuelve:
        -nada

    Las conexiones se representan con flechas que unen los dispositivos en el gráfico. 
    Los dispositivos pueden ser terminales, routers o concentradores. El nombre del 
    dispositivo puede variar dependiendo del tipo (WPAN/GPRS), y se adapta 
    automáticamente para su representación visual.

    Ejemplo de uso:
    dibujar_conexiones(conexiones_term_routersWPAN_Solucion, posiciones, 'green', 'dashed')
    """
    for conexion, valor in conexiones.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            dispositivo1, dispositivo2 = resto.split('->')
            
            # Modificar el nombre del dispositivo 2 según el tipo (WPAN/GPRS)
            if tipo == 'W':
                dispositivo2 = dispositivo2 + 'W'                
            elif tipo == 'V':
                dispositivo2 = dispositivo2 + 'G'                  
            elif tipo == 'U':
                dispositivo1 = dispositivo1 + 'W'
            elif tipo == 'R':
                dispositivo1 = dispositivo1 + 'W'  
                dispositivo2 = dispositivo2 + 'W'                  
            elif tipo == 'S':
                dispositivo1 = dispositivo1 + 'W'
                dispositivo2 = dispositivo2 + 'G'
            
            
            x1, y1 = posiciones[dispositivo1][0], posiciones[dispositivo1][1]
            x2, y2 = posiciones[dispositivo2][0], posiciones[dispositivo2][1]
            
            plt.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(
                            arrowstyle='->', color=color, linestyle=estilo))
            
    

def agrupar_conexiones(conexiones):
    """
    Agrupa las conexiones en un diccionario. Agrupando todas las conexiones
    que recibe un dispositivo en cada entrada.

    Parametros:
        - conexiones (list): Lista de conexiones a agrupar.

    Devuelve:
        - dict: Diccionario que contiene las conexiones agrupadas.
    """
    conexiones_agrupadas = {}

    for lista_conexiones in conexiones:
        for conexionCandidata in lista_conexiones:
            for nodo, valorConexion in conexionCandidata.items():
                if nodo in conexiones_agrupadas:
                    conexiones_agrupadas[nodo].append(valorConexion)
                else:
                    conexiones_agrupadas[nodo] = []
                    conexiones_agrupadas[nodo].append(valorConexion)

    return conexiones_agrupadas
    

def obtener_nodos_activos(dispositivosNombres, d_DISPOSITIVOS):
    """
    Obtiene los dispositivos activos a partir de sus nombres y soluciones.
    
    Parametros:
        - dispositivosNombres (list): Lista de nombres de dispositivos.
        - d_DISPOSITIVOS (dict): Diccionario de objetos de dispositivos.
    
    Devuelve:
        - list: Lista de nombres de dispositivos activos.
    """
    dispositivosSolucion = []
    
    for dispositivo in dispositivosNombres:
        d = d_DISPOSITIVOS[dispositivo]
        if d.solution_value() > 0:
            dispositivosSolucion.append(d.name())
    
    return dispositivosSolucion

def obtener_conexiones_activas(lista_conexiones):
    """
    Obtiene las conexiones activas a partir de una lista de conexiones.

    Parámetros:
        - conexiones (list): Lista de conexiones a evaluar.

    Returns:
        - dict: Diccionario de conexiones activas con sus valores de solución.
    """
    conexiones_activas = {}
    for conexion in lista_conexiones:
        for conn in conexion:
            c = list(conn.values())[0]
            if c.solution_value() > 0:
                conexiones_activas[c.name()] = c.solution_value()

    return conexiones_activas


def crear_variable_conexion(conn_c_D1_D2, l, solver):
    '''
    Crea y devuelve un diccionario de variables de conexión para una pareja de
    dispositivos dadas sus conexiones candidatas.
    
    Esta función genera un conjunto de variables binarias para representar la
    existencia de una conexión entre dos dispositivos (D1 y D2) sean del tipo
    que sean. Cada variable indica si existe una conexión (valor 1) o no (valor
    0).

    Parámetros:
        - conn_c_D1_D2 (list of dict):  Lista de diccionarios dónde cada
                                        elemento de la lista contiene un disp.
                                        de referencia y todos los dispositivos
                                        vecinos a los que podría conectarse.
                                        
        - l (str):  Letra que identifica el tipo de variable que va a crearse.
                    (Por ejemplo W para las conexiones entre terminales y 
                     routers WPAN)
        
        - solver (Solver):  Objeto de solver de OR-Tools para la creación de 
                            variables.
                            
                            
    Devuelve: 
        - x_conexionesD1D2 (dict):  Un diccionario de variables de OR-Tools, 
                                    donde las claves son tuplas (D1, D2) 
                                    representando una posible conexión entre un 
                                    dispositivo D1 y otro D2, y los valores son
                                    las variables binarias de OR-Tools 
                                    correspondientes a estas conexiones.
    
    Ejemplo de uso: 
        w_terminales_WPAN = crear_variable_conexion(conn_c_term_rout, 'W', solver)
   '''
   
    x_conexionesD1D2 = {}

    for conexionCandidata in conn_c_D1_D2:
        D1 = str(conexionCandidata['Referencia'][0])
        for routerCandidato in conexionCandidata["Vecinos"]:
            D2 = routerCandidato[0]
            x_conexionesD1D2[(D1, D2)] = solver.IntVar(0, 1, f'{l}_{D1}->{D2}')
            
    return x_conexionesD1D2


#%% Leemos los datos provenientes de la hoja excel

'''
#Leemos todos los datos
terminales = leerDatos('Terminales',1, 2, 4, 161, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,281,1)
concentradores = leerDatos('Ubic_Cand_Concentr',1,2,3,25,1)
'''



# Leemos menos datos para validar el modelo con menor coste computacional
terminales = leerDatos('Terminales',1, 2, 4, 40, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,15,1)
concentradores = leerDatos('Ubic_Cand_Concentr',1,2,3,10,1)



distMaxTerm = leerDatos('Distancias_Máximas',2,2,4,2,1)[0]
distMaxRout = leerDatos('Distancias_Máximas',2,3,2,3,1)[0][0]
distMaxConc = leerDatos('Distancias_Máximas',2,4,2,4,1)[0][0]


capacidadMaxWPAN = leerDatos('Capacidad_y_Coste',2,2,2,2,1)[0][0]
capacidadMaxGPRS = leerDatos('Capacidad_y_Coste',2,3,2,3,1)[0][0]
capacidadMaxConcentradores = leerDatos('Capacidad_y_Coste',2,4,2,4,1)[0][0]


costeWPAN = leerDatos('Capacidad_y_Coste',3,2,3,2,1)[0][0]
costeGPRS = leerDatos('Capacidad_y_Coste',3,3,3,3,1)[0][0]
costeConcentrador = leerDatos('Capacidad_y_Coste',3,4,3,4,1)[0][0]


# Almacenamos los nombres de todos los routers para realizar la suma de
# conexiones a cada uno de los routers
routerNombres = [fila[0] for fila in routers]
concentradorNombres = [fila[0] for fila in concentradores]
terminalNombres = [fila[0] for fila in terminales]


# Cambiamos el valor "Tipo de terminal" por su distancia máxima
for terminal in terminales:
    terminal[3] = distMaxTerm[terminal[3]-1]
    
    
    
#%% Obtenemos todas las conexiones candidatas entre dispositivos
conn_c_term_rout = dispositivos_en_rango_lista(terminales, routers)
conn_c_rout_rout = dispositivos_en_rango_lista(routers, routers, distMaxRout)
conn_c_rout_conc = dispositivos_en_rango_lista(routers, concentradores, 
                                                               distMaxConc)


#%% Definimos el modelo
solver = pywraplp.Solver.CreateSolver('SCIP')
    

# Creamos las variables conexion entre dispositivos
w_TerminalesRWPAN = crear_variable_conexion(conn_c_term_rout,'W',solver)

v_TerminalesRGPRS = crear_variable_conexion(conn_c_term_rout,'V',solver)

u_RWPANConcentradores = crear_variable_conexion(conn_c_rout_conc,'U',solver)

s_RWPAN_RGPRS = crear_variable_conexion(conn_c_rout_rout,'S',solver)

r_RWPAN_RWPAN = crear_variable_conexion(conn_c_rout_rout,'R',solver)


# Elimino las conexiones consigo mismo de un router WPAN
for router in routerNombres:
    r_RWPAN_RWPAN.pop((router,router),None)



# Creamos las variables routers gprs, wpan y concentradores. Representan el
# número de routers de cada tipo en cada posición.
# Las almacenamos en diccionarios para que sean facilmente recuperables usando
# su nombre
r_WPAN = {}
for routerWPAN in routerNombres:
    r_WPAN_VAR = solver.IntVar(0,solver.Infinity(),str(routerWPAN)+"_WPAN")
    r_WPAN[routerWPAN] = r_WPAN_VAR

r_GPRS = {}
for routerGPRS in routerNombres:
    r_GPRS_VAR = solver.IntVar(0,solver.Infinity(),routerGPRS+"_GPRS")
    r_GPRS[routerGPRS] = r_GPRS_VAR
    
c_CONCENTRADORES = {}
for concentrador in concentradorNombres:
    c_CONCENTRADOR_VAR = solver.IntVar(0,solver.Infinity(),concentrador)
    c_CONCENTRADORES[concentrador] = c_CONCENTRADOR_VAR
    

# Creamos la variable D para los routers WPAN que representa el "nivel" de un
# router WPAN. Es decir, la longitud desde un terminal hasta cada router. 
# Usamos esta variable para evitar la formación de bucles entre routers WPAN.  
D = {}
for router in routerNombres:
    D[router] = solver.NumVar(0, len(routerNombres) - 1,"D_"+router)
    
    
    

#%% Definimos las restricciones
'''
- R1:   Cada terminal solo puede estar conectado a 1 router (GPRS o WPAN)

- R2:   Cada router WPAN solo admite 5 conexiones (De terminales y otros R_WPAN)

- R3:   Cada router GPRS solo admite 10 conexiones (De terminales y R_WPAN)

- R4:   Cada Concentrador solo admite 40 conexiones (De R_WPAN)

- R5:   Un router WPAN debe ser >= que cualquiera de sus conexiones entrantes

- R6:   Un router GPRS debe ser >= que cualquiera de sus conexiones entrantes

- R7:   Un concentrador debe ser >= que cualquiera de sus conexiones entrantes

- R8:   Un router WPAN que exista, debe estar conectado a un concentrador, otro
        router WPAN o un router GPRS
        
- R9:   No pueden existir dos conexiones simultáneas identicas pero de
        dirección opuesta [R_Rx->R_Ry] y [R_Ry->R_Rx]
        
- R10:  Jerarquía de árbol
        
'''

# -R1: Cada terminal solo puede (Y DEBE) estar conectado a un router (GPRS/WPAN)
for terminal in terminalNombres:
    
    # Obtenemos todas las conexiones de un terminal a todos sus routers vecinos
    conexionesToRoutersWPAN =   { 
                                    clave: valor 
                                    for clave, valor in w_TerminalesRWPAN.items() 
                                    if clave[0] == terminal
                                }
    
    conexionesToRoutersGPRS =   { 
                                    clave: valor 
                                    for clave, valor in v_TerminalesRGPRS.items() 
                                    if clave[0] == terminal
                                }
    
    suma_WPAN = sum(valor for valor in conexionesToRoutersWPAN.values())
    suma_GPRS = sum(valor for valor in conexionesToRoutersGPRS.values())
    
    solver.Add(suma_WPAN + suma_GPRS == 1)
    
    

# Añadimos las restricciones de capacidad de los routers y concentradores    
# -R2: Capacidad máxima routers WPAN
for router in routerNombres:
    
    # Obtenemos todas las conexiones entrantes a un router
    conexionesFromTerminales =  {
                                    clave: valor 
                                    for clave, valor in w_TerminalesRWPAN.items() 
                                    if clave[1] == router        
                                }
    
    conexionesFromRouters =     {
                                    clave: valor 
                                    for clave, valor in r_RWPAN_RWPAN.items() 
                                    if clave[1] == router        
                                }
    
    suma_Terminales = sum(valor for valor in conexionesFromTerminales.values())
    suma_Routers = sum(valor for valor in conexionesFromRouters.values())

    solver.Add(suma_Terminales + suma_Routers <= capacidadMaxWPAN*r_WPAN[router])



# -R3: Capacidad máxima de routers GPRS
for router in routerNombres:
    
    # Obtenemos todas las conexiones entrantes a un router
    conexionesFromTerminales =  {
                                    clave: valor 
                                    for clave, valor in v_TerminalesRGPRS.items() 
                                    if clave[1] == router        
                                }
    
    conexionesFromRouters =     {
                                    clave: valor 
                                    for clave, valor in s_RWPAN_RGPRS.items() 
                                    if clave[1] == router        
                                }
    
    suma_Terminales = sum(valor for valor in conexionesFromTerminales.values())
    suma_Routers = sum(valor for valor in conexionesFromRouters.values())

    solver.Add(suma_Terminales + suma_Routers <= capacidadMaxGPRS*r_GPRS[router])



# -R4: Capacidad máxima concentradores
for concentrador in concentradorNombres:
    
    # Obtenemos todas las conexiones entrantes a un concentrador    
    conexionesFromRouters =     {
                                    clave: valor 
                                    for clave, valor in u_RWPANConcentradores.items() 
                                    if clave[1] == concentrador        
                                }
    
    suma_Routers = sum(valor for valor in conexionesFromRouters.values())

    solver.Add(suma_Routers <= capacidadMaxConcentradores*c_CONCENTRADORES[concentrador])
    
    
#Un router solo existirá si cualquiera de sus conexiones existe
# Es decir cada router debe ser >= a cualquiera de sus conexiones
# - R5 y R6
for router in routerNombres:
    
    # -R5: Un router WPAN debe ser >= que cualquiera de sus conexiones entrante
    conexionesFromTerminales =  {
                                    clave: valor 
                                    for clave, valor in w_TerminalesRWPAN.items() 
                                    if clave[1] == router        
                                }
    
    conexionesFromWPAN =        {
                                    clave: valor 
                                    for clave, valor in r_RWPAN_RWPAN.items() 
                                    if clave[1] == router        
                                }    
    
    for clave, conexion in conexionesFromTerminales.items():
        solver.Add(r_WPAN[router] >= conexion)
        
    for clave, conexion in conexionesFromWPAN.items():
        solver.Add(r_WPAN[router] >= conexion)
        
    
    
    
    # -R6: Un router GPRS debe ser mayor que sus conexiones entrantes 
    conexionesFromTerminales =  {
                                    clave: valor 
                                    for clave, valor in v_TerminalesRGPRS.items() 
                                    if clave[1] == router        
                                }
    
    conexionesFromWPAN =        {
                                    clave: valor 
                                    for clave, valor in s_RWPAN_RGPRS.items() 
                                    if clave[1] == router        
                                }
       
    for clave, conexion in conexionesFromTerminales.items():
        solver.Add(r_GPRS[router] >= conexion)
        
    for clave, conexion in conexionesFromWPAN.items():
        solver.Add(r_GPRS[router] >= conexion)
        



# -R7: Un concentrador solo existirá si alguna conexion entrante existe
for concentrador in concentradorNombres:
    
    conexionesFromWPAN =    {
                                clave: valor 
                                for clave, valor in u_RWPANConcentradores.items() 
                                if clave[1] == router        
                            }
    
    for clave, conexion in conexionesFromWPAN.items():
        solver.Add(c_CONCENTRADORES[concentrador] >= conexion)
        
        

# -R8: Cada router WPAN solo puede (Y DEBE) estar conectado a:
#       - O un concentrador
#       - O un router WPAN
#       - O un router GPRS
# Para que la conexión exista unicamente cuando exista el router, deberemos
# igualarlo a su existencia o no (Permite mas de una conexion saliente si hay
# mas de un router)
for router in routerNombres:
        
    # Obtenemos todas las conexiones de un terminal a todos sus routers vecinos
    conexionesToRoutersWPAN =   { 
                                    clave: valor 
                                    for clave, valor in r_RWPAN_RWPAN.items() 
                                    if clave[0] == router
                                }
    
    conexionesToRoutersGPRS =   { 
                                    clave: valor 
                                    for clave, valor in s_RWPAN_RGPRS.items() 
                                    if clave[0] == router
                                }
    
    conexionesToConcentradores ={ 
                                    clave: valor 
                                    for clave, valor in u_RWPANConcentradores.items() 
                                    if clave[0] == router
                                }
    
    suma_WPAN = sum(valor for valor in conexionesToRoutersWPAN.values())
    suma_GPRS = sum(valor for valor in conexionesToRoutersGPRS.values())
    suma_Conc = sum(valor for valor in conexionesToConcentradores.values())
    
    solver.Add(suma_WPAN + suma_GPRS + suma_Conc  == r_WPAN[router]) 
    


# -R9:  Las conexiones entre dos routers, solo pueden ser en un sentido
#       Evita la existencia simultánea de las conexiones [Rx->Ry] y [Ry->Rx]

paresConexiones = {} # Sirve para conocer si ya se ha guardado la conexion
for router1 in routerNombres:
    
    for router2 in routerNombres:
        
        # Solo añadimos la clave 1 vez. Comprobamos si ya existe el registro
        # antes de agregarla. (Asi no añadimos después dos restricciones)
        if not (router2,router1) in paresConexiones:
            
            # Manejo la excepción, por si acaso no existe la conexión.
            try:        
                conexion1 = r_RWPAN_RWPAN[router1, router2]
                conexion2 = r_RWPAN_RWPAN[router2, router1]
                suma = conexion1 + conexion2
                paresConexiones[router1, router2] = conexion1 + conexion2
                solver.Add(suma <= 1)
                    
            except KeyError:
                pass # No pasa nada si no existe la clave
                

# -R10: Diagrama jerárquico de árbol. Un router WPAN solo puede estar conectado
#       a un router que esté mas alejado de los terminales que él.
#       Dj ​>= Di​ + 1 − M*( 1 − r_RWPAN_RWPAN[i,j]​)
M = 3
for (routerO, routerD), conexion in r_RWPAN_RWPAN.items():
    solver.Add(D[routerD] >= (D[routerO] + 1 - M*(1 - conexion)))


#%% Definimos la función obejtivo y resolvemos

Z = (costeWPAN * sum(r_WPAN.values()) + costeGPRS * sum(r_GPRS.values())
                             + costeConcentrador * sum(c_CONCENTRADORES.values()))

solver.Minimize(Z)
status = solver.Solve()



#%% Procesamos la solución
if status == pywraplp.Solver.OPTIMAL:
    
    print("\nSe ha encontrado la solución óptima")
    objective = solver.Objective()
    
    '''
    routersWPANSolucion = obtener_nodos_activos(routerNombres, r_WPAN)
    routersGPRSSolucion = obtener_nodos_activos(routerNombres, r_GPRS)
    concentradoresSolucion = obtener_nodos_activos(concentradorNombres, 
                                                           c_CONCENTRADORES)
    
    print("-------------------------------------")
    


    print("Conexiones terminales-WPAN:")
    conexiones_term_routersWPAN_Solucion = obtener_conexiones_activas(
                                            w_TerminalesRWPAN)
                
    print("\nConexiones terminales-GPRS:")
    conexiones_term_routersGPRS_Solucion = obtener_conexiones_activas(
                                            v_TerminalesRGPRS)

    conexiones_routers_concentradores_Solucion = obtener_conexiones_activas(
                                        u_RWPANConcentradores)

    print("\nConexiones WPAN-WPAN")
    conexiones_routersWPAN_routersWPAN_Solucion = obtener_conexiones_activas(
                                        r_RWPAN_RWPAN)

                
    print("\nConexiones WPAN-GPRS")
    conexiones_routersWPAN_routersGPRS_Solucion = obtener_conexiones_activas(
                                            s_RWPAN_RGPRS)
    
    print("\nConexiones totales: ")
    print("terminales-WPAN = "+str(len(conexiones_term_routersWPAN_Solucion)))
    print("terminales-GPRS = "+str(len(conexiones_term_routersGPRS_Solucion)))
    print("WPAN-Concentradores = "+str(len(conexiones_routers_concentradores_Solucion)))
    print("WPAN-WPAN = "+str(len(conexiones_routersWPAN_routersWPAN_Solucion)))
    print("WPAN-GPRS = "+str(len(conexiones_routersWPAN_routersGPRS_Solucion)))
    
    print("\nNúmero de elementos totales:")
    print("Número terminales = " + str(len(terminales)))
    print("Número routers WPAN = " + str(len(routersWPANSolucion)))
    print("Número routers GPRS = " + str(len(routersGPRSSolucion)))
    print("Número concentradores = " + str(len(concentradoresSolucion)))
    
    
    print("-------------------------------------")

    '''

    costeFinal = Z.solution_value()
    print("El coste final de la infraestructura es: " + str(costeFinal))
else:
    print("El estado de la solución no es óptimo, es = " + str(status))

    

    
#%% Imprimimos un plano con todos los dispositivos, para hacernos una 
#   idea previa de la configuración del escenario.


# Pintamos en la gráfica todos los dispositivos de la red
pintar_dispositivos(1, concentradores, routers, terminales)


# Pintamos varios ejemplos con los dispositivos en rango de distintos disposit.
pintar_dispositivos_en_rango(2, 1, conn_c_term_rout)
pintar_dispositivos_en_rango(3, 1, conn_c_rout_rout, distMaxRout)
pintar_dispositivos_en_rango(4, 1, conn_c_rout_conc, distMaxConc)




    
    
        
        
        
    






























#%% Exportamos modelo
lp_model=solver.ExportModelAsLpFormat(False)
with open('modeloExportadoCasoFinalRefactorizado.txt', 'w') as f:
    print(lp_model, file=f) 





tiempoFin = time.time()

tiempo = tiempoFin - tiempoInicio


# Define las unidades de tiempo
horas = tiempo // 3600
minutos = (tiempo % 3600) // 60
segundos = tiempo % 60

# Elige la unidad para mostrar
if horas >= 1:
    print(f"Tiempo de ejecución: {horas:.0f} h, {minutos:.0f} min. y {segundos:.2f} seg.")
elif minutos >= 1:
    print(f"Tiempo de ejecución: {minutos:.0f} min. y {segundos:.2f} seg.")
else:
    print(f"Tiempo de ejecución: {segundos:.2f} seg.")




