# -*- coding: utf-8 -*-
"""
Caso final IO

Created on Fri Dec  1 11:07:33 2023

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

'''
# Leemos menos datos para validar el modelo con menor coste computacional
terminales = leerDatos('Terminales',1, 2, 4, 10, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,20,1)
concentradores = leerDatos('Ubic_Cand_Concentr',1,2,3,10,1)

'''

# Leemos menos datos para validar el modelo con menor coste computacional
terminales = leerDatos('Terminales',1, 2, 4, 5, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,14,1)
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
routersNombres = [fila[0] for fila in routers]
concentradorNombres = [fila[0] for fila in concentradores]


# Cambiamos el valor "Tipo de terminal" por su distancia máxima
for terminal in terminales:
    terminal[3] = distMaxTerm[terminal[3]-1]



#%% Obtenemos todas las conexiones candidatas entre dispositivos
conn_c_term_rout = dispositivos_en_rango_lista(terminales, routers)
conn_c_rout_rout = dispositivos_en_rango_lista(routers, routers, distMaxRout)
conn_c_rout_conc = dispositivos_en_rango_lista(routers, concentradores, distMaxConc)



#%% Imprimimos un plano con todos los dispositivos, para hacernos una 
#   idea previa de la configuración del escenario.
plt.figure(1)
plt.figure(figsize=(10, 8),dpi=150)
plt.xlim(-110, 110)
plt.ylim(-110, 110)


# Pintamos en la gráfica los 3 tipos de terminales
pintar_plano(concentradores, 'blue', 'Concentradores', marcador='o')
pintar_plano(routers, 'green', 'Routers',marcador='s')
pintar_plano(terminales, 'red', 'Terminales',marcador='*')


# Creamos una leyenda para el gráfico
concentrador_patch = mpatches.Patch(color='green', label='Concentradores (Candidatos)')
router_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
terminal_patch = mpatches.Patch(color='red', label='Terminales')
plt.legend(handles=[concentrador_patch, router_patch, terminal_patch])


# Configuraciones del gráfico
plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
plt.title('Terminales y ubicaciones candidatas de routers y concentradores')
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.grid(True)
plt.tight_layout()





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
indiceEjemplo = 0

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

print("\nDefiniendo variables conexión routers WPAN -> Concentradores:\n")
for conexionCandidata in conn_c_rout_conc:
    u_aux = []
    for concentradorCandidato in conexionCandidata["Vecinos"]:
        r = str(conexionCandidata['Referencia'][0])
        c = concentradorCandidato[0]
        variable_u = solver.IntVar(0,1,'U_'+r+'->'+c) 
        u_aux.append({str(c):variable_u})
        
    u_conexionesRoutersWPANConcentradores.append(u_aux)


imprimir_tabla_cortada(u_conexionesRoutersWPANConcentradores,"U")



# Creamos las variables de conexion router WPAN - router GPRS
s_conexionesRoutersWPANroutersGPRS = []

print("\nDefiniendo variables conexión routers WPAN -> routers GPRS:\n")
for conexionCandidata in conn_c_rout_rout:
    s_aux = []
    for routerCandidato in conexionCandidata["Vecinos"]:
        rWPAN = str(conexionCandidata['Referencia'][0])
        rGPRS = routerCandidato[0]
        variable_s = solver.IntVar(0,1,'S_'+rWPAN+'->'+rGPRS) 
        s_aux.append({str(rGPRS):variable_s})
        
    s_conexionesRoutersWPANroutersGPRS.append(s_aux)


imprimir_tabla_cortada(s_conexionesRoutersWPANroutersGPRS,"S")



# Creamos las variables de conexion router WPAN - router WPAN
r_conexionesRoutersWPANroutersWPAN = []

print("\nDefiniendo variables conexión routers WPAN -> routers WPAN:\n")
for conexionCandidata in conn_c_rout_rout:
    r_aux = []
    for routerCandidato in conexionCandidata["Vecinos"]:
        rRef = str(conexionCandidata['Referencia'][0])
        rVecino = routerCandidato[0]
        variable_r = solver.IntVar(0,1,'R_'+rRef+'->'+rVecino) 
        r_aux.append({str(rVecino):variable_r})
        
    r_conexionesRoutersWPANroutersWPAN.append(r_aux)


imprimir_tabla_cortada(r_conexionesRoutersWPANroutersWPAN,"R")



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





#%% Creamos algunas listas y diccionarios que nos serán útiles después para
#   crear variables y restricciones
'''Todo esto se podría convertir en una función'''


# Agrupamos las conexiones que llegan a cada router WPAN en un diccionario
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
                



# Agrupamos las conexiones que llegan a cada router GPRS en un diccionario
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



# Agrupamos las conexiones que llegan a cada router Concentrador en un diccionario
conexiones_routersWPAN_to_concentradores = {}

for router in u_conexionesRoutersWPANConcentradores:
    
    # Recorremos todas las conexiones posibles de cada terminal con todos
    # sus routers vecinos
    for conexionCandidata in router:
        
        # Para cada conexion, comprobamos con que router es, y la agregamos
        # al valor de suma_por_router_WPAN que corresponda a cada router
        for concentrador, valorConexion in conexionCandidata.items():
            
            # Si ya existe el router en el diccionario de sumas, sumamos
            # la variable conexion. Si no existe, la creamos
            if concentrador in conexiones_routersWPAN_to_concentradores:
                conexiones_routersWPAN_to_concentradores[concentrador].append(valorConexion)
            else:
                conexiones_routersWPAN_to_concentradores[concentrador] = []
                conexiones_routersWPAN_to_concentradores[concentrador].append(valorConexion)
                

                
# Agrupamos las conexiones que llegan a cada router Concentrador en un diccionario
conexiones_routersWPAN_to_routersWPAN = {}

for router in r_conexionesRoutersWPANroutersWPAN:
    
    # Recorremos todas las conexiones posibles de cada terminal con todos
    # sus routers vecinos
    for conexionCandidata in router:
        
        # Para cada conexion, comprobamos con que router es, y la agregamos
        # al valor de suma_por_router_WPAN que corresponda a cada router
        for routerReceptor, valorConexion in conexionCandidata.items():
            
            # Si ya existe el router en el diccionario de sumas, sumamos
            # la variable conexion. Si no existe, la creamos
            if routerReceptor in conexiones_routersWPAN_to_routersWPAN:
                conexiones_routersWPAN_to_routersWPAN[routerReceptor].append(valorConexion)
            else:
                conexiones_routersWPAN_to_routersWPAN[routerReceptor] = []
                conexiones_routersWPAN_to_routersWPAN[routerReceptor].append(valorConexion)
                
# Agrupamos las conexiones que llegan a cada router Concentrador en un diccionario
conexiones_routersWPAN_to_routersGPRS = {}

for router in s_conexionesRoutersWPANroutersGPRS:
    
    # Recorremos todas las conexiones posibles de cada terminal con todos
    # sus routers vecinos
    for conexionCandidata in router:
        
        # Para cada conexion, comprobamos con que router es, y la agregamos
        # al valor de suma_por_router_WPAN que corresponda a cada router
        for routerGPRS, valorConexion in conexionCandidata.items():
            
            # Si ya existe el router en el diccionario de sumas, sumamos
            # la variable conexion. Si no existe, la creamos
            if routerGPRS in conexiones_routersWPAN_to_routersGPRS:
                conexiones_routersWPAN_to_routersGPRS[routerGPRS].append(valorConexion)
            else:
                conexiones_routersWPAN_to_routersGPRS[routerGPRS] = []
                conexiones_routersWPAN_to_routersGPRS[routerGPRS].append(valorConexion)


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
        
'''

# -R1: Cada terminal solo puede (Y DEBE) estar conectado a un router (GPRS/WPAN)
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
    

# Añadimos las restricciones de capacidad de los routers y concentradores    
# -R2: (Capacidad máxima routers WPAN)
for router in routersNombres:
    connFromTerm = sum(conexiones_terminales_to_routerWPAN[router])
    connFromR_WPAN = sum(conexiones_routersWPAN_to_routersWPAN[router])
    solver.Add(connFromTerm + connFromR_WPAN <= capacidadMaxWPAN)

# -R3: (Capacidad máxima routers GPRS)
for router in routersNombres:
    connFromR_GPRS = sum(conexiones_terminales_to_routerGPRS[router])
    connFromR_WPAN = sum(conexiones_routersWPAN_to_routersGPRS[router])
    solver.Add(connFromR_GPRS + connFromR_WPAN <= capacidadMaxGPRS)

# -R4: (Capacidad máxima concentradores)
for concentrador in concentradorNombres:
    solver.Add(sum(conexiones_routersWPAN_to_concentradores[concentrador]) <= capacidadMaxConcentradores)

#Un router solo existirá si cualquiera de sus conexiones existe
# Es decir cada router debe ser >= a cualquiera de sus conexiones
# EJEMPLO: 
#   R1 >= W1->1
#   R1 >= W2->1
#   R1 >= W3->1
#   R1 >= W...->1
for router in routersNombres:
    
    # -R5: Un router WPAN debe ser >= que cualquiera de sus conexiones entrante
    for conexion_T_RW in conexiones_terminales_to_routerWPAN[router]:
        #print(r_WPAN[router] +" >= " + str(conexion_T_RW))
        solver.Add(r_WPAN[router] >= conexion_T_RW)

    
    # -R5': Un router WPAN debe ser >= que las conexiones con otro router WPAN
    for conexion_RW_RW in conexiones_routersWPAN_to_routersWPAN[router]:
        #print(str(r_WPAN[router]) + " >= " + str(conexion_RW_RW) )
        solver.Add(r_WPAN[router] >= conexion_RW_RW)

    
    # -R6: Un router GPRS debe ser mayor que sus conexiones entrantes    
    for conexion_T_RG in conexiones_terminales_to_routerGPRS[router]:
        #print(r_GPRS[router] +" >= " + str(conexion_T_RG))
        solver.Add(r_GPRS[router] >= conexion_T_RG)

        
    # -R6': Un router GPRS debe ser mayor que sus conexiones provenientes de
    #       otro router WPAN
    for conexion_RW_RG in conexiones_routersWPAN_to_routersGPRS[router]:
        #print(r_GPRS[router] +" >= " + str(conexion_T_RG))
        solver.Add(r_GPRS[router] >= conexion_RW_RG)
        


# -R7: Un concentrador solo existirá si cualquiera de sus conexiones entrantes existe
for concentrador in concentradorNombres:
    for conexion_R_C in conexiones_routersWPAN_to_concentradores[concentrador]:
        #print(concentrador +" >= " + str(conexion_R_C))
        solver.Add(c_CONCENTRADORES[concentrador] >= conexion_R_C)
  
        

# -R8: Cada router WPAN solo puede (Y DEBE) estar conectado a:
#       - O un concentrador
#       - O un router WPAN
#       - O un router GPRS
# Para que la conexión exista unicamente cuando exista el router, deberemos
# igualarlo a su existencia o no (que es solo 1 o 0)
for routerWPAN, routerWPAN2, routerGPRS, nombreR in zip(
                                    u_conexionesRoutersWPANConcentradores, 
                                    r_conexionesRoutersWPANroutersWPAN,
                                    s_conexionesRoutersWPANroutersGPRS,
                                    routersNombres):
        
    suma_conex_RWPAN_Concentrador = 0
    suma_conex_RWPAN_RWPAN = 0
    suma_conex_RWPAN_RGPRS = 0
    
    # Suma de todas las posibles conexiones salientes del router
    for conexionCandidata in routerWPAN:
        #print(list(conexionCandidata.values()))
        suma_conex_RWPAN_Concentrador += list(conexionCandidata.values())[0]
    
    
    '''
    for conexionCandidata in routerWPAN2:
        # No agregamos la conexión consigo mismo
        resto, rout = str(list(conexionCandidata.values())[0]).split('->')
        if str(nombreR) != rout:
            #print(list(conexionCandidata.values()))
            suma_conex_RWPAN_RWPAN += list(conexionCandidata.values())[0]
    '''
        
       
    for conexionCandidata in routerGPRS:
        # No agregamos la conexión consigo mismo
        resto, rout = str(list(conexionCandidata.values())[0]).split('->')
        if str(nombreR) != rout:
            #print(list(conexionCandidata.values()))
            suma_conex_RWPAN_RGPRS += list(conexionCandidata.values())[0]
    
    
    
    # Lo igualamos al valor de la variable que determina su existencia
    sumaTotal = (suma_conex_RWPAN_Concentrador + 
                     suma_conex_RWPAN_RWPAN + suma_conex_RWPAN_RGPRS)
    
    solver.Add(sumaTotal == r_WPAN[nombreR])    



#%% Definimos la función obejtivo y resolvemos

Z = (costeWPAN * sum(r_WPAN.values()) + costeGPRS * sum(r_GPRS.values())
                             + costeConcentrador * sum(c_CONCENTRADORES.values()))

solver.Minimize(Z)
status = solver.Solve()


#%% Procesamos la solución
if status == pywraplp.Solver.OPTIMAL:
    
    print("\nSe ha encontrado la solución óptima")
    objective = solver.Objective()
    
    print("-------------------------------------")
    print("\nDISPOSITIVOS:\n")
    print("\nRouters WPAN/Wifi activos:")
    routersWPANSolucion = []
    for router in routersNombres:
        r = r_WPAN[router]
        if r.solution_value() > 0:
            print(r.name() + " = " + str(r.solution_value()))
            routersWPANSolucion.append(r.name())
            
    
    print("\nRouters GPRS activos:")
    routersGPRSSolucion = []
    for router in routersNombres:
        r = r_GPRS[router]
        if r.solution_value() > 0:
            print(r.name() + " = " + str(r.solution_value()))
            routersGPRSSolucion.append(r.name())
     
        
    print("\nConcentradores activos:")
    concentradoresSolucion = []
    for concentrador in concentradorNombres:
        c= c_CONCENTRADORES[concentrador]
        if c.solution_value() > 0:
            print(c.name() + " = " + str(c.solution_value()))
            concentradoresSolucion.append(c.name())
            
    print("\nCONEXIONES:\n")
    print("Conexiones terminales-WPAN:")
    conexiones_term_routersWPAN_Solucion = {}
    for conexionTerminalRouter in w_conexionesTerminalesRouterWPAN:
        for conn in conexionTerminalRouter:
            c = list(conn.values())[0]
            if c.solution_value() > 0:
                print(c.name() + " = " + str(c.solution_value()))
                conexiones_term_routersWPAN_Solucion[c.name()] = c.solution_value()
                
    print("\nConexiones terminales-GPRS:")
    conexiones_term_routersGPRS_Solucion = {}
    for conexionTerminalRouter in v_conexionesTerminalesRouterGPRS:
        for conn in conexionTerminalRouter:
            c = list(conn.values())[0]
            if c.solution_value() > 0:
                print(c.name() + " = " + str(c.solution_value()))
                conexiones_term_routersGPRS_Solucion[c.name()] = c.solution_value()
                
    print("\nConexiones WPAN-Concentradores")
    conexiones_routers_concentradores_Solucion = {}
    for conexionRouterConcentrador in u_conexionesRoutersWPANConcentradores:
        for conn in conexionRouterConcentrador:
            c = list(conn.values())[0]
            if c.solution_value() > 0:
                print(c.name() + " = " + str(c.solution_value()))
                conexiones_routers_concentradores_Solucion[c.name()] = c.solution_value()
                
    print("\nConexiones WPAN-WPAN")
    conexiones_routersWPAN_routersWPAN_Solucion = {}
    for conexionRouterWPANrouterWPAN in r_conexionesRoutersWPANroutersWPAN:
        for conn in conexionRouterWPANrouterWPAN:
            c = list(conn.values())[0]
            if c.solution_value() > 0:
                print(c.name() + " = " + str(c.solution_value()))
                conexiones_routersWPAN_routersWPAN_Solucion[c.name()] = c.solution_value()
                
    print("\nConexiones WPAN-GPRS")
    conexiones_routersWPAN_routersGPRS_Solucion = {}
    for conexionRouterWPANrouterGPRS in s_conexionesRoutersWPANroutersGPRS:
        for conn in conexionRouterWPANrouterGPRS:
            c = list(conn.values())[0]
            if c.solution_value() > 0:
                print(c.name() + " = " + str(c.solution_value()))
                conexiones_routersWPAN_routersGPRS_Solucion[c.name()] = c.solution_value()
    
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
    
    
    
    
    #%% DIBUJAMOS LOS NODOS CON MATPLOTLIB
    # Extraer las posiciones de los nodos (routers, terminales y concentradores)
    # Almacenamos las posiciones de todos los nodos en un mismo array.
    # Nodo = [PosX, PosY]
    posiciones = {}
    
    for terminal in terminales:
        nombreTerminal = terminal[0]
        posX = terminal[1]
        posY = terminal[2]
        posiciones[nombreTerminal] = [posX, posY]
    
    # Solo añadimos los routers que formen parte de la solución.
    for router in routers:
        nombreRouter = str(router[0])
        if (nombreRouter+"_WPAN") in (routersWPANSolucion):
            posX = router[1]
            posY = router[2]
            posiciones[nombreRouter+"W"] = [posX, posY]
        if (nombreRouter+"_GPRS") in routersGPRSSolucion:
            posX = router[1]
            posY = router[2]
            posiciones[nombreRouter+"G"] = [posX, posY]
    
    # Solo añadimos los concentradores que formen parte de la solución
    for concentrador in concentradores:
        nombreConcentrador = str(concentrador[0])
        if nombreConcentrador in concentradoresSolucion:
            posX = concentrador[1]
            posY = concentrador[2]
            posiciones[nombreConcentrador] = [posX, posY]
            
            
        
        
    # Crear el gráfico con las mismas dimensiones y dpi que los anteriores
    plt.figure(5)
    plt.figure(figsize=(10, 8),dpi=150)

    
    
    # Dibujar los nodos
    for nodo, (x, y) in posiciones.items():
        if nodo.startswith('T'):
            plt.scatter(x, y, marker='*', color='red', label=nodo)
        elif nodo.startswith('R'):
            plt.scatter(x, y, marker='s', color='purple', label=nodo)
            ''' CREAR DISTINCION POR TIPO DE ROUTER
            elif nodo.startswith('R') and nodo in routersWPAN:
                plt.scatter(x, y, marker='s', color='purple', s=200, label=nodo)
            elif nodo.startswith('R') and nodo in routersGPRS:
                plt.scatter(x, y, marker='s', color='green', s=200, label=nodo)
            '''
        elif nodo.startswith('C'):
            plt.scatter(x, y, marker='o', color='blue', label=nodo) 
        
    
    # Dibujar las conexiones entre terminales y routers WPAN
    for conexion, valor in conexiones_term_routersWPAN_Solucion.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            terminal, router = resto.split('->')
            router = router + "W"
            x1, y1 = posiciones[terminal][0], posiciones[terminal][1]
            x2, y2 = posiciones[router][0], posiciones[router][1]
            plt.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(
                            arrowstyle='->', color='green', linestyle='dashed'))
            
    # Dibujar las conexiones entre terminales y routers GPRS
    for conexion, valor in conexiones_term_routersGPRS_Solucion.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            terminal, router = resto.split('->')
            router = router + "G"
            x1, y1 = posiciones[terminal][0], posiciones[terminal][1]
            x2, y2 = posiciones[router][0], posiciones[router][1]
            plt.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(
                            arrowstyle='->', color='green', linestyle='dashed'))
            
    # Dibujar las conexiones entre routers y concentradores
    for conexion, valor in conexiones_routers_concentradores_Solucion.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            router, concentrador = resto.split('->')
            router = router + "W"
            x1, y1 = posiciones[router][0], posiciones[router][1]
            x2, y2 = posiciones[concentrador][0], posiciones[concentrador][1]
            plt.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(
                arrowstyle='->', color='blue', linestyle='dashed'))
            
    # Dibujar las conexiones entre routersWPAN y routersWPAN
    for conexion, valor in conexiones_routersWPAN_routersWPAN_Solucion.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            router, router2 = resto.split('->')
            router = router + "W"
            router2 = router2 + "W"
            x1, y1 = posiciones[router][0], posiciones[router][1]
            x2, y2 = posiciones[router2][0], posiciones[router2][1]
            plt.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(
                arrowstyle='->', color='blue', linestyle='dashed'))
            
    # Dibujar las conexiones entre routersWPAN y routersGPRS
    for conexion, valor in conexiones_routersWPAN_routersGPRS_Solucion.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            router, router2 = resto.split('->')
            router = router + "W"
            router2 = router2 + "G"
            x1, y1 = posiciones[router][0], posiciones[router][1]
            x2, y2 = posiciones[router2][0], posiciones[router2][1]
            plt.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(
                arrowstyle='->', color='blue', linestyle='dashed'))
    
    #Creamos leyenda
    concentradores_patch = mpatches.Patch(color='blue', label='Concentradores')
    routers_patch = mpatches.Patch(color='purple', label='Routers')
    terminal_patch = mpatches.Patch(color='red', label='Routers')
    plt.legend(handles=[concentradores_patch, routers_patch, terminal_patch])
    
    
    # Configuraciones del gráfico
    plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
    plt.title('Grafo de conexiones')
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.xlim(-110, 110)
    plt.ylim(-110, 110)
    plt.grid(True)
    plt.tight_layout()


    
    
    
    #%% Dibujamos los nodos con networkx y matplotlib 
    
    # Crear un grafo
    G = nx.Graph()
    
    # Agregar nodos al grafo con atributos
    for nodo in posiciones.keys():
        if nodo.startswith('T'):
            G.add_node(nodo, node_type='terminal', color='salmon')
        elif nodo.startswith('R'):
            if nodo.endswith('W'):
                G.add_node(nodo, node_type='router_W', color='plum')
            elif nodo.endswith('G'):
                G.add_node(nodo, node_type='router_G', color='green')
            
            
        elif nodo.startswith('C'):
            G.add_node(nodo, node_type='concentrador', color='skyblue')
            
    
    # Agregar conexiones al grafo
    for conexion, valor in conexiones_term_routersWPAN_Solucion.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            terminal, router = resto.split('->')
            router = router + "W"
            G.add_edge(terminal, router, connection_type='term_router_W')
            
    for conexion, valor in conexiones_term_routersGPRS_Solucion.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            terminal, router = resto.split('->')
            router = router + "G"
            G.add_edge(terminal, router, connection_type='term_router_G')
            
    for conexion, valor in conexiones_routers_concentradores_Solucion.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            router, concentrador = resto.split('->')
            router = router + "W"
            G.add_edge(router, concentrador, connection_type='router_W_concentrador')
            
    for conexion, valor in conexiones_routersWPAN_routersGPRS_Solucion.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            router, routerG = resto.split('->')
            router = router + "W"
            routerG = routerG + "G"
            G.add_edge(router, routerG, connection_type='router_W_router_G')
            
    for conexion, valor in conexiones_routersWPAN_routersWPAN_Solucion.items():
        if valor == 1.0:
            tipo, resto = conexion.split('_')
            router, router2 = resto.split('->')
            router = router + "W"
            router2 = router2 + "W"
            G.add_edge(router, router2, connection_type='router_W_router_W')
       
        
 
    
    # Dibujar el grafo
    plt.figure(6)
    plt.figure(figsize=(10, 8),dpi=150)

    
    # Cambiamos los colores de los nodos
    node_types = nx.get_node_attributes(G, 'node_type')
    colores_nodos = []
    tam_nodos = []
    
    for nodo in G.nodes():
        if node_types[nodo] == 'terminal':
            colores_nodos.append('salmon')
            tam_nodos.append(100)
        elif node_types[nodo] == 'router_W':
            colores_nodos.append('plum')
            tam_nodos.append(400)
        elif node_types[nodo] == 'router_G':
            colores_nodos.append('LightGreen') 
            tam_nodos.append(400)
        elif node_types[nodo] == 'concentrador':
            colores_nodos.append('skyblue')
            tam_nodos.append(800)
    
            
            
    # Obtenemos los tipos de conexión para cada conexion
    connection_types = nx.get_edge_attributes(G, 'connection_type')
    # Definir colores para cada tipo de conexión
    colores_lineas = []
    for edge in G.edges():
        tipo_conexion = connection_types.get(edge, '')  #Obtiene tipo conexión
        if tipo_conexion == 'term_router_W':
            colores_lineas.append('red')
        elif tipo_conexion == 'term_router_G':
            colores_lineas.append('green')
        elif tipo_conexion == 'router_W_concentrador':
            colores_lineas.append('blue')
        elif tipo_conexion == 'router_W_router_G':
            colores_lineas.append('orange')
        elif tipo_conexion == 'router_W_router_W':
            colores_lineas.append('brown')
            
            
            
        
    # Dibujar el grafo con los nodos que tienen posición definida
    nx.draw(G, posiciones, nodelist=posiciones, edge_color= colores_lineas, 
                node_color=colores_nodos, node_size=tam_nodos,
                with_labels=True)
    

    plt.axis('on') # Forzamos que se muestren los ejes para que se vea como el resto
    plt.tick_params(axis='both', which='both', direction='inout', 
                    bottom=True, left=True)
    plt.gca().set_aspect('equal', adjustable='box') # Eje x e y proporcionales
    plt.title('Conexiones entre terminales y routers')
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.xlim(-110, 110)
    plt.ylim(-110, 110)
    plt.grid(True)    
    #plt.tight_layout()
    
    #Creamos leyenda
    routers_WPAN_patch = mpatches.Patch(color='plum', label='Routers WPAN')
    routers_GPRS_patch = mpatches.Patch(color='LightGreen', label='Routers GPRS')
    concentradores_patch = mpatches.Patch(color='skyblue', label='Concentraodres')
    terminal_patch = mpatches.Patch(color='salmon', label='Terminal')
    plt.legend(handles=[terminal_patch, routers_WPAN_patch, 
                        routers_GPRS_patch, concentradores_patch])
    
    plt.show()

    
    costeFinal = Z.solution_value()
    print("El coste final de la infraestructura es: " + str(costeFinal))
else:
    print("El estado de la solución no es óptimo, es = " + str(status))




#%% Exportamos modelo
lp_model=solver.ExportModelAsLpFormat(False)
with open('modeloExportadoCasoFinal.txt', 'w') as f:
    print(lp_model, file=f) 

tiempoFin = time.time()

tiempo = round(tiempoFin - tiempoInicio,3)

print("\nFin de la ejecución. Se completó en " + str(tiempo) +" segundos\n")









