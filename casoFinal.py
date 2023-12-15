# -*- coding: utf-8 -*-
"""
Caso final IO

Created on Fri Dec  1 11:07:33 2023

@author: jaime
"""

from ortools.linear_solver import pywraplp
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


import time

from funcionesAuxiliares import *

tiempoInicio = time.time()
print("\nInicio ejecución\n")
plt.close('All')



#%% Leemos los datos provenientes de la hoja excel

'''
#Leemos todos los datos
terminales = leerDatos('Terminales',1, 2, 4, 161, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,281,1)
concentradores = leerDatos('Ubic_Cand_Concentr',1,2,3,25,1)



# Leemos menos datos para validar el modelo con menor coste computacional
terminales = leerDatos('Terminales',1, 2, 4, 10, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,20,1)
concentradores = leerDatos('Ubic_Cand_Concentr',1,2,3,10,1)

'''

# Leemos menos datos para validar el modelo con menor coste computacional
terminales = leerDatos('Terminales',1, 2, 4, 10, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,15,1)
concentradores = leerDatos('Ubic_Cand_Concentr',1,3,3,5,1)
concentradores = []




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
conn_c_rout_conc = dispositivos_en_rango_lista(routers, concentradores, 
                                                               distMaxConc)



#%% Imprimimos un plano con todos los dispositivos, para hacernos una 
#   idea previa de la configuración del escenario.
crea_grafico(1)


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
configurar_grafico("Terminales y ubicaciones candidatas de routers " +
                   "y concentradores")





#%% Pintamos gráficos de ejemplo de conexiones candidatas.
    

#%% Pintamos routers en rango de un terminal de ejemplo para ver candidatos

indiceEjemplo = 0

terminalEjemplo = conn_c_term_rout[indiceEjemplo]["Referencia"]
distanciaMaxEjemplo = terminalEjemplo[3]
nombreTerminalEjemplo = str(terminalEjemplo[0])
routersCompatiblesEjemplo = conn_c_term_rout[indiceEjemplo]["Vecinos"]

crea_grafico(2)


# Pintamos gráfica con dispositivos
pintar_plano(routersCompatiblesEjemplo, 'blue', 'Routers',marcador='o')

pintar_nodo_rango(terminalEjemplo, distanciaMaxEjemplo)

#Creamos leyenda
routers_candidatos_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
terminal_evaluado_patch = mpatches.Patch(color='red', label='Terminal')
plt.legend(handles=[routers_candidatos_patch, terminal_evaluado_patch])

# Configuraciones del gráfico
configurar_grafico("Ubicaciones routers candidatas para conectarse con " + 
                   str(nombreTerminalEjemplo))


#%% Pintamos routers en rango de un router de ejemplo para ver candidatos
indiceEjemplo = 0

routerEjemplo = conn_c_rout_rout[indiceEjemplo]["Referencia"]
nombreRouterEjemplo = str(routerEjemplo[0])
routersCompatiblesEjemplo = conn_c_rout_rout[indiceEjemplo]["Vecinos"]

crea_grafico(3)


# Pintamos gráfica con dispositivos
pintar_plano(routersCompatiblesEjemplo, 'blue', 'Routers',marcador='o')

pintar_nodo_rango(routerEjemplo, distMaxRout)

#Creamos leyenda
routers_candidatos_patch = mpatches.Patch(color='blue', label='Routers (Candidatos)')
terminal_evaluado_patch = mpatches.Patch(color='red', label='Router referencia')
plt.legend(handles=[routers_candidatos_patch, terminal_evaluado_patch])

# Configuraciones del gráfico
configurar_grafico("Ubicaciones routers candidatas para conectarse con " +
                   "router " + str(nombreRouterEjemplo))



#%% Pintamos concentradores en rango de un router de ejemplo
indiceEjemplo = 0

routerEjemplo = conn_c_rout_conc[indiceEjemplo]["Referencia"]
nombreRouterEjemplo = str(routerEjemplo[0])
concentradoresCompatiblesEjemplo = conn_c_rout_conc[indiceEjemplo]["Vecinos"]


crea_grafico(4)

# Pintamos gráfica con dispositivos
pintar_plano(concentradoresCompatiblesEjemplo, 'green', 'Routers',marcador='s')

pintar_nodo_rango(routerEjemplo, distMaxConc)

#Creamos leyenda
routers_candidatos_patch = mpatches.Patch(color='green', 
                                          label='Concentradores (Candidatos)')

terminal_evaluado_patch = mpatches.Patch(color='red', 
                                          label='Router referencia')

plt.legend(handles=[routers_candidatos_patch, terminal_evaluado_patch])



# Configuraciones del gráfico
configurar_grafico("Ubicaciones concentradores candidatas para conectarse con " +
                   "router " + str(nombreRouterEjemplo))


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

#print(w_conexionesTerminalesRouterWPAN)


'''          
print(routers_dict)
print()
print(routers_dict['R1'])
'''



print("\nDefiniendo variables conexión terminal -> routers WPAN:\n")
#imprimir_tabla_cortada(w_conexionesTerminalesRouterWPAN,"W")



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

#imprimir_tabla_cortada(v_conexionesTerminalesRouterGPRS,"V")



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


#imprimir_tabla_cortada(u_conexionesRoutersWPANConcentradores,"U")



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


#imprimir_tabla_cortada(s_conexionesRoutersWPANroutersGPRS,"S")



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


#imprimir_tabla_cortada(r_conexionesRoutersWPANroutersWPAN,"R")
#w_conexionesTerminalesRouterWPAN_DICT = generar_diccionario_variables_conn(
#                                                    conn_c_term_rout, solver)

'''
print("\nw_conexionesTerminaleRouterWPAN")
print(w_conexionesTerminalesRouterWPAN)
print("\nw_conexionesTerminaleRouterWPAN_DICT")
print(w_conexionesTerminalesRouterWPAN_DICT)
print()


conexiones_terminales_to_routerWPAN_DICT = reorganiza_dict(w_conexionesTerminalesRouterWPAN_DICT)

print(conexiones_terminales_to_routerWPAN_DICT)

routers_dict = {}

# Iterar a través del diccionario original
for terminal, rout in w_conexionesTerminalesRouterWPAN_DICT.items():
    # Iterar a través de los routers asociados a cada terminal
    for router, value in rout.items():
        # Verificar si el router ya existe en el diccionario reorganizado
        if router not in routers_dict:
            # Si no existe, crear una entrada para ese router y agregar el terminal y su valor
            routers_dict[router] = {terminal: value}
        else:
            # Si el router ya existe, agregar el terminal y su valor al diccionario existente
            routers_dict[router][terminal] = value


print()
'''


# Creamos las variables routers gprs, wpan y concentradores. 1 por cada uno.
# Las almacenamos en diccionarios para que sean facilmente recuperables usando
# su nombre
r_WPAN = {}
for routerWPAN in routers:
    r_WPAN_VAR = solver.IntVar(0,solver.Infinity(),str(routerWPAN[0])+"_WPAN")
    r_WPAN[routerWPAN[0]] = r_WPAN_VAR

r_GPRS = {}
for routerGPRS in routers:
    r_GPRS_VAR = solver.IntVar(0,solver.Infinity(),str(routerGPRS[0])+"_GPRS")
    r_GPRS[routerGPRS[0]] = r_GPRS_VAR
    
c_CONCENTRADORES = {}
for concentrador in concentradores:
    c_CONCENTRADOR_VAR = solver.IntVar(0,solver.Infinity(),concentrador[0])
    c_CONCENTRADORES[concentrador[0]] = c_CONCENTRADOR_VAR
    

print(str(len(r_WPAN)) + " posiciones candidatas para routers WPAN")
print(str(len(r_GPRS)) + " posiciones candidatas para routers GPRS")
print(str(len(c_CONCENTRADORES)) + " posiciones candidatas para concentradores")





#%% Creamos algunas listas y diccionarios que nos serán útiles después para
#   crear variables y restricciones

conexiones_terminales_to_routerWPAN = agrupar_conexiones(
                                        w_conexionesTerminalesRouterWPAN)

conexiones_terminales_to_routerGPRS = agrupar_conexiones(
                                        v_conexionesTerminalesRouterGPRS)

conexiones_routersWPAN_to_concentradores = agrupar_conexiones(
                                        u_conexionesRoutersWPANConcentradores)

conexiones_routersWPAN_to_routersWPAN = agrupar_conexiones(
                                        r_conexionesRoutersWPANroutersWPAN)

conexiones_routersWPAN_to_routersGPRS = agrupar_conexiones(
                                        s_conexionesRoutersWPANroutersGPRS)

'''
print()
print(conexiones_terminales_to_routerWPAN['R1'])
print()
print(list(routers_dict['R1'].values()))
'''

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
        
- R10:  Lo que entra en un router WPAN debe ser igual a lo que sale
        
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
print("R_WPAN")
print(r_WPAN)
for router in routersNombres:
    connFromTerm = sum(conexiones_terminales_to_routerWPAN[router])
    connFromR_WPAN = sum(conexiones_routersWPAN_to_routersWPAN[router])
    '''¿Habría que sumar también las conexiones salientes?'''
    print(router)
    solver.Add(connFromTerm + connFromR_WPAN <= 
                           capacidadMaxWPAN * r_WPAN[router])

# -R3: (Capacidad máxima routers GPRS)
for router in routersNombres:
    connFromR_GPRS = sum(conexiones_terminales_to_routerGPRS[router])
    connFromR_WPAN = sum(conexiones_routersWPAN_to_routersGPRS[router])
    solver.Add(connFromR_GPRS + connFromR_WPAN 
                   <= capacidadMaxGPRS * r_GPRS[router])

# -R4: (Capacidad máxima concentradores)
for concentrador in concentradorNombres:
    solver.Add(sum(conexiones_routersWPAN_to_concentradores[concentrador]) 
                <= capacidadMaxConcentradores * c_CONCENTRADORES[concentrador])

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
    
    
    ''' DESACTIVAMOS CONEXIONES ENTRE ROUTERS WPAN
    for conexionCandidata in routerWPAN2:
        # No agregamos la conexión consigo mismo
        resto, rout = str(list(conexionCandidata.values())[0]).split('->')
        #if str(nombreR) != rout:
            #print(list(conexionCandidata.values()))
            #suma_conex_RWPAN_RWPAN += list(conexionCandidata.values())[0]
    '''
    
        
       
    for conexionCandidata in routerGPRS:
        # No agregamos la conexión consigo mismo
        resto, rout = str(list(conexionCandidata.values())[0]).split('->')
        #if str(nombreR) != rout:
            #print(list(conexionCandidata.values()))
            #suma_conex_RWPAN_RGPRS += list(conexionCandidata.values())[0]
    
    
    
    # Lo igualamos al valor de la variable que determina su existencia
    sumaTotal = (suma_conex_RWPAN_Concentrador + 
                     suma_conex_RWPAN_RWPAN + suma_conex_RWPAN_RGPRS)
    
    solver.Add(sumaTotal == r_WPAN[nombreR])  
    
    
    
    
# -R9:  Las conexiones entre dos routers, solo pueden ser en un sentido
#       Evita la existencia simultánea de las conexiones [Rx->Ry] y [Ry->Rx]
parejas_valores = []

for conexion1 in r_conexionesRoutersWPANroutersWPAN:
    for router_dict1 in conexion1:
        router1, valor1 = list(router_dict1.items())[0]
        resto1, Rorigen1 = str(valor1).split('_')
        Rorigen1, Rdestino1 = Rorigen1.split('->')

        for conexion2 in r_conexionesRoutersWPANroutersWPAN:
            for router_dict2 in conexion2:
                router2, valor2 = list(router_dict2.items())[0]
                resto2, Rorigen2 = str(valor2).split('_')
                Rorigen2, Rdestino2 = Rorigen2.split('->')

                if Rorigen1 == Rdestino2 and Rdestino1 == Rorigen2:
                    parejas_valores.append([valor1, valor2])
                    break

for pareja in parejas_valores:
    resto, nombreRouter = str(pareja[0]).split('_')
    nombreRouter, resto = nombreRouter.split('->')
    
    solver.Add(sum(pareja) <= r_WPAN[nombreRouter])
    
    
# -R10: Las conexiones entrantes en un router WPAN deben ser iguales a las salientes
'''
for router, conexionesSalientesR, conexionesSalientesS, conexionesSalientesU in zip(
        routersNombres, r_conexionesRoutersWPANroutersWPAN,
        s_conexionesRoutersWPANroutersGPRS, u_conexionesRoutersWPANConcentradores):
    
    connFromTerm = sum(conexiones_terminales_to_routerWPAN[router])
    connFromR_WPAN = sum(conexiones_routersWPAN_to_routersWPAN[router])
    conexionesIN = connFromTerm + connFromR_WPAN
    
    valoresConexionesOUT_W = [list(dic.values())[0] for dic in conexionesSalientesR]
    valoresConexionesOUT_G = [list(dic.values())[0] for dic in conexionesSalientesS] 
    valoresConexionesOUT_C = [list(dic.values())[0] for dic in conexionesSalientesU] 
    
    connToR_WPAN= sum(valoresConexionesOUT_W)
    connToR_GPRS= sum(valoresConexionesOUT_G)
    connToC_CONC= sum(valoresConexionesOUT_C)
    
    
    
    
    
    conexionesOUT = 5*(connToR_WPAN + connToR_GPRS + connToC_CONC) #+ r_WPAN[router])
  

    solver.Add(conexionesIN <= conexionesOUT)

'''
                

            




#%% Definimos la función obejtivo y resolvemos

Z = (costeWPAN * sum(r_WPAN.values()) + costeGPRS * sum(r_GPRS.values())
                             + costeConcentrador * sum(c_CONCENTRADORES.values()))

solver.Minimize(Z)
status = solver.Solve()


#%% Procesamos la solución
if status == pywraplp.Solver.OPTIMAL:
    
    print("\nSe ha encontrado la solución óptima")
    objective = solver.Objective()
    
    routersWPANSolucion = obtener_nodos_activos(routersNombres, r_WPAN)
    routersGPRSSolucion = obtener_nodos_activos(routersNombres, r_GPRS)
    concentradoresSolucion = obtener_nodos_activos(concentradorNombres, 
                                                           c_CONCENTRADORES)
    
    
    # Extraer las posiciones de los nodos (routers, terminales y concentradores)
    # Almacenamos las posiciones de todos los nodos en un mismo array.
    # Nodo = [PosX, PosY]
    posiciones = {}
    
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
    
    print("\nPosiciones dispositivos solucion")
    print(posiciones)
    
    for terminal in terminales:
        nombreTerminal = terminal[0]
        posX = terminal[1]
        posY = terminal[2]
        posiciones[nombreTerminal] = [posX, posY]
            
    
    print("-------------------------------------")


    print("Conexiones terminales-WPAN:")
    conexiones_term_routersWPAN_Solucion = obtener_conexiones_activas(
                                            w_conexionesTerminalesRouterWPAN)
    print(conexiones_term_routersWPAN_Solucion)
                
    print("\nConexiones terminales-GPRS:")
    conexiones_term_routersGPRS_Solucion = obtener_conexiones_activas(
                                            v_conexionesTerminalesRouterGPRS)
    
    print(conexiones_term_routersGPRS_Solucion)
    
    print("\nConexiones WPAN-Concentradores")
    conexiones_routers_concentradores_Solucion = obtener_conexiones_activas(
                                        u_conexionesRoutersWPANConcentradores)
    print(conexiones_routers_concentradores_Solucion)
    

    print("\nConexiones WPAN-WPAN")
    conexiones_routersWPAN_routersWPAN_Solucion = obtener_conexiones_activas(
                                        r_conexionesRoutersWPANroutersWPAN)
    print(conexiones_routersWPAN_routersWPAN_Solucion)

                
    print("\nConexiones WPAN-GPRS")
    conexiones_routersWPAN_routersGPRS_Solucion = obtener_conexiones_activas(
                                            s_conexionesRoutersWPANroutersGPRS)
    print(conexiones_routersWPAN_routersGPRS_Solucion)
    
    
    
    print("\nConexiones totales: ")
    print("terminales-WPAN = "+str(len(conexiones_term_routersWPAN_Solucion)))
    print("terminales-GPRS = "+str(len(conexiones_term_routersGPRS_Solucion)))
    print("WPAN-Concentradores = "+str(len(conexiones_routers_concentradores_Solucion)))
    print("WPAN-WPAN = "+str(len(conexiones_routersWPAN_routersWPAN_Solucion)))
    print("WPAN-GPRS = "+str(len(conexiones_routersWPAN_routersGPRS_Solucion)))
    
    print("\nNúmero de elementos totales:")
    print("Número terminales = " + str(len(terminales)))
    print("\nNúmero routers WPAN = " + str(len(routersWPANSolucion)))
    print(routersWPANSolucion)
    print("\nNúmero routers GPRS = " + str(len(routersGPRSSolucion)))
    print(routersGPRSSolucion)
    print("\nNúmero concentradores = " + str(len(concentradoresSolucion)))
    print(concentradoresSolucion)
    
    
    print("-------------------------------------")
    
    
    
    
    #%% DIBUJAMOS LOS NODOS CON MATPLOTLIB        
        
    # Crear el gráfico con las mismas dimensiones y dpi que los anteriores
    crea_grafico(5)

    
    
    # Dibujar los nodos y las conexiones
    dibujar_nodos_con_texto(posiciones)
    
    dibujar_conexiones(conexiones_term_routersWPAN_Solucion, posiciones, 
                       'red', 'dashed')
    
    dibujar_conexiones(conexiones_term_routersGPRS_Solucion, posiciones, 
                       'green', 'dashed')
    
    dibujar_conexiones(conexiones_routers_concentradores_Solucion, posiciones, 
                       'blue', 'dashed')
    
    dibujar_conexiones(conexiones_routersWPAN_routersWPAN_Solucion, posiciones, 
                       'brown', 'dashed')
    
    dibujar_conexiones(conexiones_routersWPAN_routersGPRS_Solucion, posiciones, 
                       'orange', 'dashed')

    
    
    #Creamos leyenda
    routers_WPAN_patch = mpatches.Patch(color='plum', label='Routers WPAN')
    routers_GPRS_patch = mpatches.Patch(color='LightGreen', label='Routers GPRS')
    concentradores_patch = mpatches.Patch(color='skyblue', label='Concentraodres')
    terminal_patch = mpatches.Patch(color='salmon', label='Terminal')
    plt.legend(handles=[terminal_patch, routers_WPAN_patch, 
                        routers_GPRS_patch, concentradores_patch])
    
    
    # Configuraciones estandar del gráfico
    configurar_grafico("Grafo de conexiones 1")


    
    
    
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
                G.add_node(nodo, node_type='router_G', color='LightGreen')
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
    crea_grafico(6)

    
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
    configurar_grafico("Grafo de conexiones 2",0)
    
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









