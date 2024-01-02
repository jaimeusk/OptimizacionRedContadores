# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 11:07:33 2023

Caso Final. Refactorizado

@author: jaime
"""



from ortools.linear_solver import pywraplp
import matplotlib.pyplot as plt
import time #Se usa para medir el tiempo de ejecución
import os   #Se usa para crear la carpeta en la que almacenar las soluciones
import webbrowser #Se usa para abrir al final de la ejecución el informe html

# Librerías gráficas para crear plots e informe html
from imprimeGraficos import (pintar_dispositivos,                             
                             crea_grafico_conexiones_1,
                             crea_grafico_conexiones_2,
                             imprime_html,
                             generar_tabla_html,
                             generar_tabla_html2,
                             genera_graficos_conexiones)


# Librerías con utilidades para el manejo de los datos
from utilidades import (dispositivos_en_rango_lista, 
                        leerDatos, 
                        obtener_nodos_activos, 
                        obtener_conexiones_activas,
                        crear_variable_conexion,
                        crea_posiciones)

tiempoInicio = time.time()
print("\nInicio ejecución\n")
plt.close('All')
plt.ioff() # Evitamos que los gráficos se muestren por defecto

           
 
    

#%% Leemos los datos provenientes de la hoja excel


#Leemos todos los datos
terminales = leerDatos('Terminales',1, 2, 4, 161, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,281,1)
concentradores = leerDatos('Ubic_Cand_Concentr',1,2,3,25,1)


'''
# Leemos menos datos para validar el modelo con menor coste computacional
terminales = leerDatos('Terminales',1, 2, 4, 70, 1)
routers = leerDatos('Ubic_Cand_Routers',1,2,3,15,1)
concentradores = leerDatos('Ubic_Cand_Concentr',1,2,3,10,1)
'''



distMaxTerm = leerDatos('Distancias_Máximas',2,2,4,2,1)[0]
distMaxRout = leerDatos('Distancias_Máximas',2,3,2,3,1)[0][0]
distMaxConc = leerDatos('Distancias_Máximas',2,4,2,4,1)[0][0]



capacidadMaxWPAN = leerDatos('Capacidad_y_Coste',2,2,2,2,1)[0][0]
capacidadMaxGPRS = leerDatos('Capacidad_y_Coste',2,3,2,3,1)[0][0]
capacidadMaxConcentradores = leerDatos('Capacidad_y_Coste',2,4,2,4,1)[0][0]


costeWPAN = leerDatos('Capacidad_y_Coste',3,2,3,2,1)[0][0]
costeGPRS = leerDatos('Capacidad_y_Coste',3,3,3,3,1)[0][0]
costeConcentrador = leerDatos('Capacidad_y_Coste',3,4,3,4,1)[0][0]


# Almacenamos los nombres de todos los routers y concentradores para facilitar
# después el manejo de los datos.
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
#solver = pywraplp.Solver('Example', pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING)
solver = pywraplp.Solver.CreateSolver('SCIP')
    

# Creamos las variables conexion entre dispositivos
w_TerminalesRWPAN = crear_variable_conexion(conn_c_term_rout,'W',solver)
v_TerminalesRGPRS = crear_variable_conexion(conn_c_term_rout,'V',solver)
u_RWPANConcentradores = crear_variable_conexion(conn_c_rout_conc,'U',solver)
s_RWPAN_RGPRS = crear_variable_conexion(conn_c_rout_rout,'S',solver)
r_RWPAN_RWPAN = crear_variable_conexion(conn_c_rout_rout,'R',solver)


# Eliminamos las conexiones consigo mismo de un router WPAN
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

WPAN = costeWPAN * sum(r_WPAN.values())
GPRS = costeGPRS * sum(r_GPRS.values())
conc = costeConcentrador * sum(c_CONCENTRADORES.values())
                     
Z = WPAN + GPRS + conc

solver.Minimize(Z)
status = solver.Solve()

   

#%% Procesamos la solución
if status == pywraplp.Solver.OPTIMAL:
    
    print("\nSe ha encontrado la solución óptima")
    costeFinal = Z.solution_value()
    print("El coste final de la infraestructura es: " + str(costeFinal))
    

    # Almacenamos en estas nuevas variables unicamente las variables 
    # "activas", es decir, aquellas que no son 0
    routersWPANSolucion = obtener_nodos_activos(routerNombres, r_WPAN)
    routersGPRSSolucion = obtener_nodos_activos(routerNombres, r_GPRS)
    concentradoresSolucion = obtener_nodos_activos(concentradorNombres, 
                                                           c_CONCENTRADORES)
    
    w_TerminalesRWPAN_Solucion = obtener_conexiones_activas(w_TerminalesRWPAN)
    v_TerminalesRGPRS_Solucion = obtener_conexiones_activas(v_TerminalesRGPRS)
    u_RWPANConcentradores_Solucion = obtener_conexiones_activas(u_RWPANConcentradores)
    r_RWPAN_RWPAN_Solucion = obtener_conexiones_activas(r_RWPAN_RWPAN)
    s_RWPAN_RGPRS_Solucion = obtener_conexiones_activas(s_RWPAN_RGPRS)
    
    
    
    # Generar y almacenar gráficos para mostrar en el informe HTML    
    genera_graficos_conexiones(w_TerminalesRWPAN_Solucion, 
                                   conn_c_term_rout, distMax = 0)
    genera_graficos_conexiones(v_TerminalesRGPRS_Solucion, 
                                   conn_c_term_rout, distMax = 0)
    genera_graficos_conexiones(s_RWPAN_RGPRS_Solucion, 
                                   conn_c_rout_rout, distMax = distMaxRout)
    genera_graficos_conexiones(r_RWPAN_RWPAN_Solucion, 
                                   conn_c_rout_rout, distMax = distMaxRout)
    genera_graficos_conexiones(u_RWPANConcentradores_Solucion, 
                                   conn_c_rout_conc, distMax = distMaxConc)
    
    
    
    # Creamos los dos gráficos.
    posiciones = crea_posiciones(terminales, routers, concentradores,
                        routersWPANSolucion, routersGPRSSolucion,
                        concentradoresSolucion)
    
    
    
    # Generamos los gráficos de los concentradores que aparecen en la solución
    G1 = crea_grafico_conexiones_1(5, posiciones,
                                  w_TerminalesRWPAN_Solucion,
                                  v_TerminalesRGPRS_Solucion, 
                                  u_RWPANConcentradores_Solucion,
                                  r_RWPAN_RWPAN_Solucion,
                                  s_RWPAN_RGPRS_Solucion)
    
    G2 = crea_grafico_conexiones_2(6, posiciones, 
                                  w_TerminalesRWPAN_Solucion,
                                  v_TerminalesRGPRS_Solucion, 
                                  u_RWPANConcentradores_Solucion,
                                  r_RWPAN_RWPAN_Solucion,
                                  s_RWPAN_RGPRS_Solucion)
    
    posicionesTermWPAN = crea_posiciones(terminales = terminales,
                                         routers= routers,
                                         routersWPANSolucion = routersWPANSolucion)
    
    posicionesTermGPRS = crea_posiciones(terminales = terminales,
                                         routers= routers,
                                         routersGPRSSolucion = routersGPRSSolucion)
    
    
    posicionesWpanConc = crea_posiciones(routers= routers, concentradores = concentradores,
                                         routersWPANSolucion = routersWPANSolucion,
                                         concentradoresSolucion=concentradoresSolucion)
    
    posicionesWpanGPRS = crea_posiciones(routers= routers,
                                         routersWPANSolucion = routersWPANSolucion,
                                         routersGPRSSolucion = routersGPRSSolucion)   
    
    posicionesWpanWpan = crea_posiciones(routers= routers,
                                         routersWPANSolucion = routersWPANSolucion)
                                         
    
    GTermWPAN = crea_grafico_conexiones_1(7, posicionesTermWPAN, 
                        w_TerminalesRWPAN_Solucion=w_TerminalesRWPAN_Solucion)
    GTermGPRS = crea_grafico_conexiones_1(8, posicionesTermGPRS, 
                        v_TerminalesRGPRS_Solucion=v_TerminalesRGPRS_Solucion)
    
    GWPANConc = crea_grafico_conexiones_1(9, posicionesWpanConc, 
                u_RWPANConcentradores_Solucion=u_RWPANConcentradores_Solucion)
    GWPANWPAN = crea_grafico_conexiones_1(10, posicionesWpanWpan, 
                r_RWPAN_RWPAN_Solucion=r_RWPAN_RWPAN_Solucion)
    GWPANGPRS = crea_grafico_conexiones_1(11, posicionesWpanGPRS, 
                s_RWPAN_RGPRS_Solucion=s_RWPAN_RGPRS_Solucion)
    
    
    
    # Para crear una gráfica por cada tipo de dispositivo, hacemos lo siguiente:
    # eliminar el sufijo "_GPRS"
    routersSinGPRS = [router.replace('_GPRS', '') for router in routersGPRSSolucion]
    routersSinWPAN = [router.replace('_GPRS', '') for router in routersWPANSolucion]
    
    routersGPRSPintar = [router for router in routers if router[0] in routersSinGPRS]
    routersWPANPintar = [router for router in routers if router[0] in routersSinGPRS]
    concentradoresPintar = [concentrador for concentrador in concentrador if concentrador[0] in concentradoresSolucion]
    
    # Garantizamos antes de guardar las imágenes, la existencia del directorio
    directorio_salida = "graficosSolucion"
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)  
    
    
    GDispCompletos = pintar_dispositivos(1,
    "Posiciones terminales y posiciones candidatas de routers y concentradores", 
    concentradores, routers, terminales)
    GDispCompletos.savefig("graficosSolucion/posicionesTotales.png")
    
    GDispRoutersGPRS = pintar_dispositivos(2,"Posiciones routers GPRS solución", routers = routersGPRSPintar)
    GDispRoutersGPRS.savefig("graficosSolucion/solucionGPRS.png")
    
    GDispRoutersWPAN = pintar_dispositivos(2,"Posiciones routers WPAN solución", routers = routersWPANPintar)
    GDispRoutersWPAN.savefig("graficosSolucion/solucionWPAN.png")
    
    GDispConcentradores = pintar_dispositivos(2,"Posiciones concentradores solución", concentradores = concentradoresPintar)
    GDispConcentradores.savefig("graficosSolucion/solucionConcentradores.png")
    
    GDispTerminales = pintar_dispositivos(2,"Posiciones terminales", terminales = terminales)
    GDispTerminales.savefig("graficosSolucion/solucionTerminales.png")
    
    
    
    
    G1.savefig("graficosSolucion/solucionConexiones1.png")
    G2.savefig("graficosSolucion/solucionConexiones2.png")
    
    GTermWPAN.savefig("graficosSolucion/solucionConexiones3.png")
    GTermGPRS.savefig("graficosSolucion/solucionConexiones4.png")
    GWPANConc.savefig("graficosSolucion/solucionConexiones5.png")    
    GWPANWPAN.savefig("graficosSolucion/solucionConexiones6.png")
    GWPANGPRS.savefig("graficosSolucion/solucionConexiones7.png")
    
    
    # Datos para la tabla de conexiones por tipo
    conexiones_tipo = [
        ["Term-RWPAN", len(w_TerminalesRWPAN_Solucion),"graficosSolucion/solucionConexiones3.png"],
        ["Term-RGPRS", len(v_TerminalesRGPRS_Solucion),"graficosSolucion/solucionConexiones4.png"],
        ["RWPAN-Conc.", len(u_RWPANConcentradores_Solucion),"graficosSolucion/solucionConexiones5.png"],
        ["RWPAN-RWPAN", len(r_RWPAN_RWPAN_Solucion),"graficosSolucion/solucionConexiones6.png"],
        ["RWPAN-RGPRS", len(s_RWPAN_RGPRS_Solucion),"graficosSolucion/solucionConexiones7.png"]
    ]

    # Datos para la tabla de número de dispositivos por tipo [Nu]
    dispositivos_tipo = [
        ["Nº Term.", len(terminales),"graficosSolucion/solucionTerminales.png"],
        ["Nº RWPAN", len(routersWPANSolucion),"graficosSolucion/solucionWPAN.png"],
        ["Nº RGPRS", len(routersGPRSSolucion),"graficosSolucion/solucionGPRS.png"],
        ["Nº Conc.", len(concentradoresSolucion),"graficosSolucion/solucionConcentradores.png"]
    ]

    # Imprimiendo las tablas
    
    tablaConexiones = generar_tabla_html2(conexiones_tipo, ["Conexiones", "Ud."])
    tablaDispositivos = generar_tabla_html2(dispositivos_tipo, ["Dispositivo", "Ud."])
    
    
    # Generamos informe en HTML con todos los gráficos de la solución

    html_tabla_w = generar_tabla_html(w_TerminalesRWPAN_Solucion, 
                                      ["Terminal", "R - WPAN", "Valor"])
    html_tabla_v = generar_tabla_html(v_TerminalesRGPRS_Solucion, 
                                      ["Terminal", "R - GPRS", "Valor"])
    html_tabla_u = generar_tabla_html(u_RWPANConcentradores_Solucion, 
                                      ["R - WPAN", "Concent,", "Valor"])
    html_tabla_r = generar_tabla_html(r_RWPAN_RWPAN_Solucion, 
                                      ["R - WPAN", "R - WPAN", "Valor"])
    html_tabla_s = generar_tabla_html(s_RWPAN_RGPRS_Solucion, 
                                      ["R - WPAN", "R - GPRS", "Valor"])
    
    
    
    # Generamos código HTML
    html_final = imprime_html(tablaConexiones, "Resumen conexiones","graficosSolucion/solucionConexiones1.png",
                              tabla2=tablaDispositivos, 
                              titulo2="Resumen dispositivos",enlace2="graficosSolucion/posicionesTotales.png",
                              solucionOptima= costeFinal, html=None)
    html_final = imprime_html(html_tabla_w, 
                    "Terminales a routers WPAN","graficosSolucion/solucionConexiones3.png",
                    html=html_final)
    html_final = imprime_html(html_tabla_v, 
                    "Terminales a routers GPRS", "graficosSolucion/solucionConexiones4.png",
                    html=html_final)
    html_final = imprime_html(html_tabla_r, 
                    "Routers WPAN routers WPAN","graficosSolucion/solucionConexiones6.png",
                    html=html_final)
    html_final = imprime_html(html_tabla_s, 
                    "Routers WPAN routers GPRS","graficosSolucion/solucionConexiones7.png",
                    html=html_final)
    html_final = imprime_html(html_tabla_u, 
                    "Routers WPAN a Concentradores","graficosSolucion/solucionConexiones5.png",
                    html=html_final)
    
    
    
    
    # Escribe el contenido HTML en un archivo
    with open('informe.html', 'w') as file:
        file.write(html_final)

    
    
    directorio = str(os.getcwd())
    url = directorio + '/informe.html'
    webbrowser.open(url)
    
else:
    print("El estado de la solución no es óptimo, es = " + str(status))

    


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




