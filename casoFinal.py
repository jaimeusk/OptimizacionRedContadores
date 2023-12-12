# -*- coding: utf-8 -*-
"""
Caso final IO

Created on Fri Dec  1 11:07:33 2023

@author: jaime
"""

import pandas as pd
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from tabulate import tabulate
import math

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

def pintar_plano(dispositivos, color, tipo, marcador='o'):
    """
    Pinta grafica dispositivos en un plano.
    
    Argumentos:
    - dispositivos (list): Lista de dispositivos con sus coordenadas.
    - color (str): Color de los dispositivos en el gráfico.
    - tipo (str): Tipo de dispositivo (para la leyenda).
    - marcador (str, opcional): Tipo de marcador ('o' por defecto para círculos).
                               Puede ser 'o' para círculos, '*' para estrellas, 's' para cuadrados, etc.
    
    Devuelve:
        Nada
    """
    
    for dispositivo in dispositivos:
        x, y = dispositivo[1], dispositivo[2]
        plt.scatter(x, y, color=color, marker=marcador)
        plt.text(x, y, dispositivo[0], fontsize=6, ha='right')
        

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
    

#%% Leemos los datos provenientes de la hoja excel
'''
terminales = leerDatos('Terminales',1, 2, 4, 161, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,281,1)
concentradores = leerDatos('Ubic_Cand_Concentr',1,2,3,25,1)
'''

# Leemos menos datos para validar el modelo con menor coste computacional
terminales = leerDatos('Terminales',1, 2, 4, 10, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,20,1)
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
# Cambiamos el valor "Tipo de terminal" por su distancia máxima
for terminal in terminales:
    terminal[3] = distMaxTerm[terminal[3]-1]


#%% Imprimimos un plano con todos los dispositivos, para hacernos una 
#   idea previa de la configuración del escenario.
plt.figure(1)
plt.figure(figsize=(10, 8),dpi=150)
plt.xlim(-110, 110)
plt.ylim(-110, 110)


# Pintamos en la gráfica los 3 tipos de terminales
pintar_plano(concentradores, 'green', 'Concentradores', marcador='s')
pintar_plano(routers, 'blue', 'Routers',marcador='o')
pintar_plano(terminales, 'red', 'Terminales',marcador='*')


# Creamos una leyenda para el gráfico
concentrador_patch = mpatches.Patch(color='green', label='Concentradores (Candidatos)')
router_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
terminal_patch = mpatches.Patch(color='red', label='Terminales')
plt.legend(handles=[concentrador_patch, router_patch, terminal_patch])


# Configuraciones del gráfico
plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
plt.title('Ubicaciones candidatas de Dispositivos')
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.grid(True)
plt.tight_layout()



#%% Obtenemos todas las conexiones candidatas entre dispositivos
conn_c_term_rout = dispositivos_en_rango_lista(terminales, routers)
conn_c_rout_rout = dispositivos_en_rango_lista(routers, routers, distMaxRout)
conn_c_rout_conc = dispositivos_en_rango_lista(routers, concentradores, distMaxConc)


#%% Pintamos gráficos de ejemplo de conexiones candidatas.
    

#%% Pintamos routers en rango de un terminal de ejemplo para ver candidatos
indiceEjemplo = 0

terminalEjemplo = conn_c_term_rout[indiceEjemplo]["Referencia"]
distanciaMaxEjemplo = terminalEjemplo[3]
nombreTerminalEjemplo = str(terminalEjemplo[0])
routersCompatiblesEjemplo = conn_c_term_rout[indiceEjemplo]["Vecinos"]

plt.figure(2)
plt.figure(figsize=(10, 8),dpi=150)
plt.xlim(-110, 110)
plt.ylim(-110, 110)

# Pintamos gráfica con dispositivos
pintar_plano(routersCompatiblesEjemplo, 'blue', 'Routers',marcador='o')

pintar_nodo_rango(terminalEjemplo, distanciaMaxEjemplo)

#Creamos leyenda
routers_candidatos_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
terminal_evaluado_patch = mpatches.Patch(color='red', label='Terminal')
plt.legend(handles=[routers_candidatos_patch, terminal_evaluado_patch])

# Configuraciones del gráfico
plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
plt.title('Ubicaciones routers candidatas para conectarse con '+ nombreTerminalEjemplo)
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.grid(True)
plt.tight_layout()


#%% Pintamos routers en rango de un router de ejemplo para ver candidatos
indiceEjemplo = 7

routerEjemplo = conn_c_rout_rout[indiceEjemplo]["Referencia"]
nombreRouterEjemplo = str(routerEjemplo[0])
routersCompatiblesEjemplo = conn_c_rout_rout[indiceEjemplo]["Vecinos"]

plt.figure(3)
plt.figure(figsize=(10, 8),dpi=150)
plt.xlim(-110, 110)
plt.ylim(-110, 110)


# Pintamos gráfica con dispositivos
pintar_plano(routersCompatiblesEjemplo, 'blue', 'Routers',marcador='o')

pintar_nodo_rango(routerEjemplo, distMaxRout)

#Creamos leyenda
routers_candidatos_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
terminal_evaluado_patch = mpatches.Patch(color='red', label='Router referencia')
plt.legend(handles=[routers_candidatos_patch, terminal_evaluado_patch])

# Configuraciones del gráfico
plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
plt.title('Ubicaciones routers candidatas para conectarse con router '+ nombreRouterEjemplo)
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.grid(True)
plt.tight_layout()



#%% Pintamos concentradores en rango de un router de ejemplo
indiceEjemplo = 10

routerEjemplo = conn_c_rout_conc[indiceEjemplo]["Referencia"]
nombreRouterEjemplo = str(routerEjemplo[0])
concentradoresCompatiblesEjemplo = conn_c_rout_conc[indiceEjemplo]["Vecinos"]

plt.figure(4)
plt.figure(figsize=(10, 8),dpi=150)
plt.xlim(-110, 110)
plt.ylim(-110, 110)


# Pintamos gráfica con dispositivos
pintar_plano(concentradoresCompatiblesEjemplo, 'green', 'Routers',marcador='s')

pintar_nodo_rango(routerEjemplo, distMaxConc)

#Creamos leyenda
routers_candidatos_patch = mpatches.Patch(color='green', label='Concentradores (Candidatos)')
terminal_evaluado_patch = mpatches.Patch(color='red', label='Router referencia')
plt.legend(handles=[routers_candidatos_patch, terminal_evaluado_patch])

# Configuraciones del gráfico
plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
plt.title('Ubicaciones concentradores candidatas para conectarse con router '+ nombreRouterEjemplo)
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.grid(True)
plt.tight_layout()


#%% Definimos el modelo
solver = pywraplp.Solver.CreateSolver('SCIP')



# Creamos las variables de conexión terminales-router WPAN
# Solamente crearemos las fisicamente posibles para cada terminal
w_conexionesTerminalesRouterWPAN = []

for conexionCandidata in conn_c_term_rout:
    w_aux = []
    for routerCandidato in conexionCandidata["Vecinos"]:
        t = str(conexionCandidata['Referencia'][0])
        r = routerCandidato[0]
        variable_w = solver.IntVar(0,1,'W_'+t+'->'+r)
        w_aux.append({str(r):variable_w})
        
    w_conexionesTerminalesRouterWPAN.append(w_aux)


print("\nDefiniendo variables conexión terminal -> routers WPAN:\n")
print("La estructura es la siguiente:")
print(" - Cada fila contiene las conexiones candidatas de un terminal con todos" + 
      " los routers a su alcance.")
print(" - La referencia {Rxx : W_yy->R_xx} sirve para posteriormente recuperar" + 
      " las conexiones de un router con todos los terminales haciendo uso de" +
      " la referencia R_xx\n")

imprimir_tabla_cortada(w_conexionesTerminalesRouterWPAN,"W")



# Creamos las variables de conexión terminales-router GPRS
# Solamente crearemos las fisicamente posibles para cada terminal
v_conexionesTerminalesRouterGPRS = []

print("\nDefiniendo variables conexión terminal -> routers GPRS:\n")
for conexionCandidata in conn_c_term_rout:
    v_aux = []
    for routerCandidato in conexionCandidata["Vecinos"]:    
        t = str(conexionCandidata['Referencia'][0])
        r = routerCandidato[0]
        variable_v = solver.IntVar(0,1,'V_'+t+'->'+r)
        v_aux.append({str(r):variable_v})   #Lo agregamos como diccionario para
                                            # poder recuperarlo por routers después.
    
    v_conexionesTerminalesRouterGPRS.append(v_aux)

imprimir_tabla_cortada(v_conexionesTerminalesRouterGPRS,"V")



# Creamos las variables de conexión router WPAN-Concentrador
# Solamente crearemos las fisicamente posibles para cada router
u_conexionesRoutersWPANConcentradores = []

print("\nDefiniendo variables conexión routers GPRS -> Concentradores:\n")
for conexionCandidata in conn_c_rout_conc:
    u_aux = []
    for concentradorCandidato in conexionCandidata["Vecinos"]:
        r = str(conexionCandidata['Referencia'][0])
        c = concentradorCandidato[0]
        variable_u = solver.IntVar(0,1,'U_'+r+'->'+c) 
        u_aux.append({str(c):variable_u})
        
    u_conexionesRoutersWPANConcentradores.append(u_aux)


imprimir_tabla_cortada(u_conexionesRoutersWPANConcentradores,"U")



# Creamos las variables routers gprs, wpan y concentradores. 1 por cada uno.
# Las almacenamos en diccionarios para que sean facilmente recuperables usando
# su nombre
r_WPAN = {}
for routerWPAN in routers:
    r_WPAN_VAR = solver.IntVar(0,1,str(routerWPAN[0])+"_WPAN")
    r_WPAN[routerWPAN[0]] = r_WPAN_VAR

r_GPRS = {}
for routerGPRS in routers:
    r_GPRS_VAR = solver.IntVar(0,1,str(routerGPRS[0])+"_GPRS")
    r_GPRS[routerGPRS[0]] = r_GPRS_VAR
    
c_CONCENTRADORES = {}
for concentrador in concentradores:
    c_CONCENTRADOR_VAR = solver.IntVar(0,1,concentrador[0])
    c_CONCENTRADORES[concentrador[0]] = c_CONCENTRADOR_VAR


print(str(len(r_WPAN)) + " posiciones candidatas para routers WPAN")
print(str(len(r_GPRS)) + " posiciones candidatas para routers GPRS")
print(str(len(c_CONCENTRADORES)) + " posiciones candidatas para concentradores")


#%% Definimos las restricciones
'''
- R1: Cada terminal solo puede estar
'''

#%% Cada terminal solo puede estar conectado a un router (GPRS o WPAN)
for terminal_WPAN, terminal_GPRS in zip(w_conexionesTerminalesRouterWPAN, 
                                        v_conexionesTerminalesRouterGPRS):
    sum_conex_terminal_RWPAN = 0
    sum_conex_terminal_RGPRS = 0
    
    for conexionCandidata in terminal_WPAN:
        sum_conex_terminal_RWPAN += list(conexionCandidata.values())[0]
    
    for conexionCandidata in terminal_GPRS:
        sum_conex_terminal_RGPRS += list(conexionCandidata.values())[0]
    
    suma = sum_conex_terminal_RWPAN + sum_conex_terminal_RGPRS
    solver.Add(suma == 1)






# Almacenamos los nombres de todos los routers para realizar la suma de
# conexiones a cada uno de los routers
routersNombres = [fila[0] for fila in routers]

#%% Cada Router WPAN solo puede recibir 5 conexiones de terminales

'''

BORRAR TODO ESTE COMENTARIO

# Creamos un diccionario en el que almacenar la suma de cada router
suma_por_router_WPAN = {}

# Recorremos fila a fila todas las conexiones entre terminales y routers
for terminal in w_conexionesTerminalesRouterWPAN:
    
    # Recorremos todas las conexiones posibles de cada terminal con todos
    # sus routers vecinos
    for conexionCandidata in terminal:
        
        # Para cada conexion, comprobamos con que router es, y la agregamos
        # al valor de suma_por_router_WPAN que corresponda a cada router
        for router, valorConexion in conexionCandidata.items():
            
            # Si ya existe el router en el diccionario de sumas, sumamos
            # la variable conexion. Si no existe, la creamos
            if router in suma_por_router_WPAN:
                suma_por_router_WPAN[router] += valorConexion
            else:
                suma_por_router_WPAN[router] = valorConexion
    

for router in routersNombres:
    solver.Add(suma_por_router_WPAN[router] <= capacidadMaxWPAN)
    
print(suma_por_router_WPAN)  

#%% Cada router GPRS solo puede recibir 10 conexiones de terminales
# Creamos un diccionario en el que almacenar la suma de cada router
suma_por_router_GPRS = {}

# Recorremos fila a fila todas las conexiones entre terminales y routers
for terminal in v_conexionesTerminalesRouterGPRS:
    
    # Recorremos todas las conexiones posibles de cada terminal con todos
    # sus routers vecinos
    for conexionCandidata in terminal:
        
        # Para cada conexion, comprobamos con que router es, y la agregamos
        # al valor de suma_por_router_WPAN que corresponda a cada router
        for router, valorConexion in conexionCandidata.items():
            
            # Si ya existe el router en el diccionario de sumas, sumamos
            # la variable conexion. Si no existe, la creamos
            if router in suma_por_router_GPRS:
                suma_por_router_GPRS[router] += valorConexion
            else:
                suma_por_router_GPRS[router] = valorConexion

for router in routersNombres:
    solver.Add(suma_por_router_GPRS[router] <= capacidadMaxGPRS)
    
BORRAR
'''    

#%% Agrupamos las conexiones que llegan a cada router en un diccionario
conexiones_terminales_to_routerWPAN = {}

for terminal in w_conexionesTerminalesRouterWPAN:
    
    # Recorremos todas las conexiones posibles de cada terminal con todos
    # sus routers vecinos
    for conexionCandidata in terminal:
        
        # Para cada conexion, comprobamos con que router es, y la agregamos
        # al valor de suma_por_router_WPAN que corresponda a cada router
        for router, valorConexion in conexionCandidata.items():
            
            # Si ya existe el router en el diccionario de sumas, sumamos
            # la variable conexion. Si no existe, la creamos
            if router in conexiones_terminales_to_routerWPAN:
                conexiones_terminales_to_routerWPAN[router].append(valorConexion)
            else:
                conexiones_terminales_to_routerWPAN[router] = []
                conexiones_terminales_to_routerWPAN[router].append(valorConexion)
                



conexiones_terminales_to_routerGPRS = {}

for terminal in v_conexionesTerminalesRouterGPRS:
    
    # Recorremos todas las conexiones posibles de cada terminal con todos
    # sus routers vecinos
    for conexionCandidata in terminal:
        
        # Para cada conexion, comprobamos con que router es, y la agregamos
        # al valor de suma_por_router_WPAN que corresponda a cada router
        for router, valorConexion in conexionCandidata.items():
            
            # Si ya existe el router en el diccionario de sumas, sumamos
            # la variable conexion. Si no existe, la creamos
            if router in conexiones_terminales_to_routerGPRS:
                conexiones_terminales_to_routerGPRS[router].append(valorConexion)
            else:
                conexiones_terminales_to_routerGPRS[router] = []
                conexiones_terminales_to_routerGPRS[router].append(valorConexion)


#%% Añadimos las restricciones de capacidad de los routers
for router in routersNombres:
    solver.Add(sum(conexiones_terminales_to_routerGPRS[router]) <= capacidadMaxGPRS)
    
for router in routersNombres:
    solver.Add(sum(conexiones_terminales_to_routerWPAN[router]) <= capacidadMaxWPAN)

#%% Un router solo existirá si cualquiera de sus conexiones existe
# Es decir cada router debe ser >= a cualquiera de sus conexiones
# EJEMPLO: 
#   R1 >= W1->1
#   R1 >= W2->1
#   R1 >= W3->1
#   R1 >= W...->1
for router in routersNombres:
    for conexion in conexiones_terminales_to_routerWPAN[router]:
        solver.Add(r_WPAN[router] >= conexion)
        
for router in routersNombres:
    for conexion in conexiones_terminales_to_routerGPRS[router]:
        solver.Add(r_GPRS[router] >= conexion)
        
#%% Un concentrador solo existirá si cualquiera de sus conexiones entrantes existe







#%% Exportamos modelo
lp_model=solver.ExportModelAsLpFormat(False)
with open('modeloExportadoCasoFinal.txt', 'w') as f:
    print(lp_model, file=f) 

print("\nFin de la ejecución")






