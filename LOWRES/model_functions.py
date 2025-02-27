
def time_discretization(h_s, h_f, time_divisions, factor_low_res, lowres):
    # Hora de inicio y final de la jornada
    time_window = (h_s,h_f)     

    # Intervalos que servirán para la discretización 
    time_intervals = [ time_window[0] + i*(time_window[1]-time_window[0])/time_divisions for i in range(time_divisions) ]
    time_intervals.append(h_f)
    time_dic = {i: (j,time_intervals[i+1]) for i, j in enumerate(time_intervals) if i+1<len(time_intervals) }
    list_time = list(time_dic.keys())

    if lowres == True:
        list_time_low_res = [ i for i in list_time if i%factor_low_res == 0 ]
    else:
        list_time_low_res = []
        
    delta = (time_window[1]-time_window[0])/time_divisions

    return time_window, time_intervals, time_dic, list_time, delta, list_time_low_res


def len_trip(i,T_passenger_stations, coord_passenger_stations):
    '''
    Calcula la distancia en norma manhattan de un viaje
    '''
    stat_i = T_passenger_stations[i][0]
    stat_f = T_passenger_stations[i][1]
    xy_stat_i = coord_passenger_stations[stat_i]
    xy_stat_f = coord_passenger_stations[stat_f]
    x_stat_i = xy_stat_i[0]
    y_stat_i = xy_stat_i[1]
    x_stat_f = xy_stat_f[0]
    y_stat_f = xy_stat_f[1]

    return  abs(x_stat_f - x_stat_i) + abs(y_stat_f-y_stat_i)


def distance(i, j, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations):
    '''
    Calcula distancia entre el final del viaje i y el inicio del viaje j si i,j pertenecen a Travels.
    No es conmutativo, con i en Travels y s en Stations_chrg: 
        - distance(i,s) devuelve distancia entre la estación de pasajeros final de i con la estación 
        de carga s.
        - distance(s,i) devuelve distancia entre la estación de carga s con la estación de pasajeros 
        inicial de i
    '''
    if i!=j:
        if i in Travels:
            x_ini = coord_passenger_stations[T_passenger_stations[i][1]][0]
            y_ini = coord_passenger_stations[T_passenger_stations[i][1]][1]
        elif i in Depots:
            x_ini = coord_depots[i][0]
            y_ini = coord_depots[i][1]    
        elif i in Stations_chrg:
            x_ini = coord_charge_stations[i][0]
            y_ini = coord_charge_stations[i][1]
        #--------------------------------

        if j in Travels:
            x_fin = coord_passenger_stations[T_passenger_stations[j][0]][0]
            y_fin = coord_passenger_stations[T_passenger_stations[j][0]][1]
        elif j in Depots:
            x_fin = coord_depots[j][0]
            y_fin = coord_depots[j][1]    
        elif j in Stations_chrg:
            x_fin = coord_charge_stations[j][0]
            y_fin = coord_charge_stations[j][1]
        #--------------------------------
        return abs(x_fin-x_ini)+abs(y_fin-y_ini) #norma Manhattan
    else:
        return 0
    

def estimate_time(Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations, speed_bus):
    # Estima el tiempo entre dos nodos en función de la distancia entre ellos.

    TDS = Travels+Depots+Stations_chrg
    t = {(i, j):round(distance(i,j, Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)/speed_bus,2) for i in TDS for j in TDS}
    return t


def cost_fuel(Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, T_ab, coord_depots, coord_charge_stations, h_inv, A, A1, A2, A3, A4, A5, A6, A7, cost_per_distance, fuel_per_distance):
    '''
    Se estima por medio de la distancia el costo y el combustible que necesita cada viaje
    '''
    fuel_requirement = {i:fuel_per_distance*len_trip(i,T_passenger_stations, coord_passenger_stations) for i in Travels}
    cost = {}
    fuel = {}
    for arc in A:
        if arc in A1+A2:
            cost[arc] = cost_per_distance*distance(arc[0],arc[1], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
            fuel[arc] = fuel_requirement[arc[0]] + fuel_per_distance*distance(arc[0],arc[1], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
        if arc in A3:
            cost[arc] = cost_per_distance*distance(h_inv[arc[1]][0],h_inv[arc[1]][1][0], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
            fuel[arc] = fuel_requirement[h_inv[arc[1]][0]] +  fuel_per_distance*distance(h_inv[arc[1]][0],h_inv[arc[1]][1][0], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
        if arc in A4+A5:
            cost[arc] = cost_per_distance*distance(h_inv[arc[0]][1][0],arc[1], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
            fuel[arc] = fuel_per_distance*distance(h_inv[arc[0]][1][0],arc[1], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
        if arc in A6:
            cost[arc] = cost_per_distance*distance(arc[0],arc[1], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
            fuel[arc] = fuel_per_distance*distance(arc[0],arc[1], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
        if arc in A7:
            cost[arc] = cost_per_distance*distance(h_inv[arc[1]][0],h_inv[arc[1]][1][0], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
            fuel[arc] = fuel_per_distance*distance(h_inv[arc[1]][0],h_inv[arc[1]][1][0], Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations)
            
    return cost, fuel


