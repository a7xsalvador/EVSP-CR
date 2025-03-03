#para construir instancias aleatorias
import random 
import model_functions as mf

def generate_data(seed, num_travels, num_depots, num_charge_stations, num_passenger_stations, size_square, v_max, v_min, time_window, max_capacity_charge_station, min_capacity_charge_station, list_time, speed_bus, dic_time_lr, lowres):
    '''
    Genera datos aleatorios para coordenadas de las estaciones de pasajero, 
    depósitos y estaciones de carga devolviendo un diccionario con viajes 
    alatorios entre dos estaciones de pasajeros aleatorias y un diccionario con
    las horas de salida y de llegada de cada viaje.
    '''
    
    random.seed(seed)
    
    Travels = list(range(1,num_travels+1))
    Depots = [depot+num_travels for depot in range(1,num_depots+1)]                # n+1,n+2,...,n+size_K
    Stations_chrg = [num_travels+num_depots+s for s in range(1,num_charge_stations+1)]
    Stations_chrg_time = [(s,time) for s in Stations_chrg for time in list_time]

    
    dic_Stations_chrg_time_low_res = {}

    for key, value in dic_time_lr.items():
        dic_Stations_chrg_time_low_res[key] =  [(s,time) for s in Stations_chrg for time in value] if lowres == True else []


    #------ EMPIEZA GENERACION ALEATORIA

    # Las estaciones de pasajeros empiezan desde 0, 
    # Los depósitos y estaciones de carga desde su respectivo indice dado en Depots y Stations_chrg
    coord_passenger_stations = {i:(round(random.uniform(0,size_square),0),round(random.uniform(0,size_square),0)) for i in range(num_passenger_stations)}
    coord_depots = {i:(round(random.uniform(0,size_square),0),round(random.uniform(0,size_square),0)) for i in Depots}
    coord_charge_stations = {i:(round(random.uniform(0,size_square),0),round(random.uniform(0,size_square),0)) for i in Stations_chrg}

    D_v = {i:random.randint(v_min, v_max) for i in Depots }
    
    list_stations = range(num_passenger_stations)

    T_passenger_stations = {
        i: tuple(random.sample(list_stations, 2))
        for i in Travels
        if len(list_stations) >= 2 # Garantiza poder tomar 2 elementos
    }# Devuelve aleatoriamente viajes {viaje_i:(estacion inicial, estacion final)}

    
    # Separa el tiempo desde las time_window[0] hasta las time_window[1], ese intervalo se divide para el numero de viajes y
    # cada viaje se lo asigna en orden y con esos intervalos luego el tiempo de finalización esta dado por tiempo (redondeado) del viaje
    # (i-1) para empezar desde el tiempo time_window[0]
    delta = (time_window[1]-time_window[0])/num_travels
    T_ab = {i: (  round(time_window[0]+(i-1)*delta,2) , round(time_window[0]+(i-1)*delta  + mf.len_trip(i,T_passenger_stations,coord_passenger_stations)/speed_bus,2) ) for i in Travels}
    
    rs_kt = {(k,t): random.randint(min_capacity_charge_station,max_capacity_charge_station) for k in Stations_chrg for t in list_time} # rs_kt devuelve la capacidad de la estacion k en el tiempo t

    return Travels, Depots, Stations_chrg, Stations_chrg_time, coord_passenger_stations, coord_depots, coord_charge_stations, T_passenger_stations, T_ab, D_v, rs_kt, dic_Stations_chrg_time_low_res