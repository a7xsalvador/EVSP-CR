import random 

#EJEMPLO PAPER

def data_paper(size_square,seed):
    random.seed(seed)

    #Datos para replicar el grafo del paper
    num_travels = 2
    num_depots = 1
    num_charge_stations = 2
    num_passenger_stations = 4

    Travels = list(range(1,num_travels+1))
    Depots = [depot+num_travels for depot in range(1,num_depots+1)]                #n+1,n+2,...,n+size_K
    Stations_chrg = [num_travels+num_depots+s for s in range(1,num_charge_stations+1)]

    ## Data input para ejemplo del paper.

    # estaciones para el viaje i (estacion inicial, estacion final) tomadas de las estaciones [1,2,3,4]
    T_passenger_stations = {1:(1,2), 2:(2,3)}

    # tiempos para el viaje i (inicio, final)  {i:(a_i,b_i)}
    T_ab = {1:(0,5), 2:(10,15)}# viaje 1, a_1 =0, b_1=5

    #Depósitos y capacidades de los depósitos v_k {k:v_k}
    D_v = {1:2}

    coord_passenger_stations = {i:(round(random.uniform(0,size_square),0),round(random.uniform(0,size_square),0)) for i in range(num_passenger_stations)}
    coord_depots = {i:(round(random.uniform(0,size_square),0),round(random.uniform(0,size_square),0)) for i in Depots}
    coord_charge_stations = {i:(round(random.uniform(0,size_square),0),round(random.uniform(0,size_square),0)) for i in Stations_chrg}

    #ingresando compatibilidad manualmente
    dic_comp = { i:[] for i in Travels } 
    dic_comp[1] = [2]
    dic_comp_F = { (i,j):[ ] for i in Travels+Depots for j in Travels + Depots} #le hago diccionari
    dic_comp_F[1,2] = [4,5]
    dic_comp_F[3,2] = [4,5]
    dic_comp_F[3,1] = [4,5]

    return Travels, Depots, Stations_chrg, coord_passenger_stations, coord_depots, coord_charge_stations, T_passenger_stations, T_ab, D_v, dic_comp, dic_comp_F
