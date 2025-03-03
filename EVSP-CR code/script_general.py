from model_functions import time_discretization, len_trip, distance, estimate_time, cost_fuel
from compatibility_functions import compatibility, comp_T
#from data_paper import data_paper
from graph_construction import create_nodes, create_archs
from plot_functions import plot_city, plot_graph
from generate_data import generate_data
from initial_model import initial_model
from lp_functions import from_V_to_TDS, calculate_cost, calculate_fuel
from export_data import export_data
import random
import gurobipy as gp
import time

#gp.setParam('OutputFlag', 0)


def script_general(lowres, seed,K,num_travels,num_depots,num_charge_stations,num_passenger_stations,w,speed_bus,fuel_per_distance,cost_per_distance,h_s,h_f,time_divisions,v_max,v_min,size_square,max_capacity_charge_station,min_capacity_charge_station, factor_low_res ):

    inicio_global = time.time()

    (time_window,
    time_intervals, 
    time_dic, 
    list_time,
    delta,
    list_time_low_res)              = time_discretization(h_s, h_f, time_divisions, factor_low_res, lowres)

    fin1 = time.time()
    print(f"time discretization completed in {fin1 - inicio_global}")

    #Se genera datos para una instancia.
    (Travels, 
    Depots, 
    Stations_chrg, 
    Stations_chrg_time, 
    coord_passenger_stations, 
    coord_depots, 
    coord_charge_stations, 
    T_passenger_stations, 
    T_ab, 
    D_v,
    rs_kt,
    Stations_chrg_time_low_res)                 = generate_data(seed, num_travels, num_depots, num_charge_stations, num_passenger_stations, size_square, v_max, v_min, time_window, max_capacity_charge_station, min_capacity_charge_station, list_time, speed_bus, list_time_low_res, lowres)

    fin2 = time.time()
    print(f"generate data completed in {fin2 - fin1}")

    # Se calcula el tiempo entre estaciones viajes, depósitos y estaciones de carga.
    t                       = estimate_time(Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, coord_depots, coord_charge_stations, speed_bus)

    (H_list,
    H_list_inv,
    h, 
    h_inv,
    V,
    V_visual,
    Stations_chrg_time_dic,
    Stations_chrg_time_dic_inv,
    Stations_chrg_time_dic_inv_low_res) = create_nodes(Travels, Depots, Stations_chrg_time, num_travels, num_depots,num_charge_stations, Stations_chrg_time_low_res, lowres )

    fin3 = time.time()
    print(f"create nodes completed in {fin3-fin2}")


    #Se calcula las compatibilidades.
    (dic_comp, 
    dic_comp_F,
    list_comp_FT)            = compatibility(Travels, Depots, Stations_chrg, Stations_chrg_time, T_passenger_stations, T_ab, t, time_dic)

    fin4 = time.time()
    print(f"compatibilities completed in {fin4-fin3}")

    Hk = {k:[h[h_node] for h_node in H_list if h_node[0] in Travels+[k] ] for k in Depots}

    (A1, 
     A2, 
     A3, 
     A4, 
     A5, 
     A6, 
     A7,
     A, 
     A_list,
     delta_mas,
     delta_menos,
     Ak,
     cost,
     fuel,
     A4_prepared,
     A4_dic_preparated,
     Ak_with_i_in_DH, 
     Ak_with_i_not_in_DH, 
     delta_mas_i, 
     delta_mas_k, 
     delta_mas_h)                = create_archs(Travels, Depots, h, H_list, dic_comp, dic_comp_F, T_ab, time_dic, t, Hk, fuel_per_distance, T_passenger_stations, coord_passenger_stations, Stations_chrg, coord_depots, coord_charge_stations, cost_per_distance )

    fin5 = time.time()
    print(f"create archs completed in {fin5-fin4}")

    #Se estiman los costos y el combustible.
   # (cost,
   # fuel)                   = cost_fuel(Travels, Depots, Stations_chrg, coord_passenger_stations, T_passenger_stations, T_ab, coord_depots, coord_charge_stations, h_inv, A, A1, A2, A3, A4, A5, A6, A7, cost_per_distance, fuel_per_distance)
    
    fin6 = time.time()
    print(f"cost and fuel completed in {fin6-fin5}")

    #export_data(num_travels,time_dic,w,seed,V,T_ab,D_v,h_inv,rs_kt,cost,fuel,A1,A2,A3,A4,A5,A6,A7)



    #------------------------------ MODELO BASADO EN ARCOS

    # M1

    fuel_accumulated = 0 
    for (i,j) in A:
        fuel_accumulated += fuel[(i,j)]
    M1 = 2*fuel_accumulated
    finM1 = time.time()
    print(f'M1 en {finM1-fin6}')

    # M2
    tmax = max(list(t.values()))
    bmax = max([ ab[1] for ab in list(T_ab.values())])
    M2 = 2*tmax + K*w + bmax

    finM2 = time.time()
    print(f'M2 en {finM2-finM1}')

    # para hacer un multigrafo, se debe dividir el conjunto de H porque no debe contener todos los depósitos para una copia k del grafo
    Travels_and_k = {k: Travels + [k] for k in Depots}
    #Hk = {k:[h[h_node] for h_node in H_list if h_node[0] in Travels_and_k[k] ] for k in Depots}

    finHk = time.time()
    print(f'Hk en {finHk-finM2}')


    Nodes_k = {k: Travels+[k]+Hk[k] for k in Depots}
    #Ak = [(i, j, k) for (i,j) in A for k in Depots if i in Travels+[k]+Hk[k] and j in Travels+[k]+Hk[k]]
    #Ak = [(i, j, k) for (i,j) in A for k in Depots if i in Nodes_k[k] and j in Nodes_k[k]]

    #Akk = {k : (i,j) for (i,j) in A for k in Depots if i in Nodes_k[k] and j in Nodes_k[k]}


    finAk = time.time()
    print(f'Ak en {finAk-finHk}')

    #original
    #delta_mas= { (i,k) : [ j1 for (i1,j1,k1) in Ak if i1 == i and k == k1] for i in V for k in Depots}
    #delta_menos= { (j,k) : [ i1 for (i1,j1,k1) in Ak if j1 == j and k == k1 ] for j in V for k in Depots}

    
    finDeltas = time.time()
    #print(f'Deltas en {finDeltas-finAk}')

    Hk_complete = {k:[h_arch for h_arch in H_list if h_arch[0] in Travels_and_k[k] ] for k in Depots}

    finHkComplete = time.time()
    print(f'Hk_complete en {finHkComplete-finDeltas}')

    H_stk = { (s1,t1,k1): [h[key] for key in Hk_complete[k1] if key[1] == (s1,t1)] for (s1,t1) in Stations_chrg_time for k1 in Depots}
    H_T = { i:[h[index] for index in H_list if index[0] == i  ] for i in Travels}


    inicio2 = time.time()

    print(f"el resto... en {inicio2-finHkComplete}")


    # Crear el objeto del modelo
    model2 = gp.Model()

    # Definir las variables de decisión
    x = model2.addVars(Ak, vtype=gp.GRB.BINARY, name='x')
    F = model2.addVars(V, lb = 0, ub = w, vtype=gp.GRB.CONTINUOUS, name='F')


    # Definir la función objetivo 
    model2.setObjective(gp.quicksum(cost[(arco[0],arco[1])]*x[arco] for arco in Ak ), sense=gp.GRB.MINIMIZE)


    # Restricciones

    DH = Depots + H_list_inv

    # Primera restricción: se deben satisfacer todos los viajes
    model2.addConstrs((gp.quicksum(x[(i,j,k)] for k in Depots for j in delta_mas[(i,k)] ) == 1 for i in Travels), name = '1ra_restr')

    # Segunda restricción: se respeta la capacidad del depósito
    model2.addConstrs((gp.quicksum(x[(k,j,k)] for j in delta_mas[k,k]) <= D_v[k] for k in Depots), name = '2da_restr')
        
    # Tercera restricción: conservación de flujo
    model2.addConstrs((gp.quicksum(x[(j,i,k)] for j in delta_menos[(i,k)]) - gp.quicksum(x[(i,j,k)] for j in delta_mas[(i,k)]) == 0 for k in Depots for i in Nodes_k[k]), name = '3ra_restr')

    # Cuarta restricción: capacidad de las estaciones de carga
    #model2.addConstrs((gp.quicksum(x[(h1, j, k)] for h1 in H_st[(s1, t1)] for k in Depots for j in delta_mas[h1,k] ) <= rs_kt[(s1, t1)] for s1 in Stations_chrg for t1 in list_time), name='4ta_restr')
    model2.addConstrs((gp.quicksum(x[(h1, j, k)] for k in Depots for h1 in H_stk[(s1, t1, k)] for j in delta_mas[h1,k]  ) <= rs_kt[(s1, t1)] for s1 in Stations_chrg for t1 in list_time), name='4ta_restr')

    # Quinta restricción: 
    model2.addConstrs((F[j] >= F[i] + fuel[(i,j)] - (1-x[(i,j,k)])*M1 for (i,j,k) in Ak_with_i_not_in_DH), name = '5ta_restr')

    # Sexta restricción: 
    model2.addConstrs((F[j] >= fuel[(i,j)] - (1-x[(i,j,k)])*M1 for (i,j,k) in Ak_with_i_in_DH ), name = '6ta_restr')

    fin_sexta = time.time()
    print(f'todas las restricciones menos la septima en {fin_sexta-inicio2}')

    # Séptima restricción 
#    for (h1, j) in A:
#        if h1 in H_list_inv and j in Travels :
#            model2.addConstr( time_window[0] + delta*(h_inv[h1][1][1] + 1) + K*F[h1] + t[(h_inv[h1][1][0], j)] 
#                                <= T_ab[j][0] + (1 - gp.quicksum(x[(h1,j,k2)] for k2 in Depots if (h1,j,k2) in Ak ))*M2 , name=f'7ma_restr_{j}_{h1}' )

    for (h1, j, s_t) in A4_prepared:
        model2.addConstr( time_window[0] + delta*(s_t[1] + 1) + K*F[h1] + t[(s_t[0], j)] 
                        <= T_ab[j][0] + (1 - gp.quicksum(x[(h1,j,k2)] for k2 in A4_dic_preparated[(h1,j)] ))*M2 , name=f'7ma_restr_{j}_{h1}' )



    fin_septima = time.time()
    print(f'la septima en {fin_septima-fin_sexta}')



    #model2.Params.OutputFlag = 0
    model2.Params.LogFile = f'logs_new/salida_modelo_arcos_{num_travels}_{seed}.log'
    model2.Params.TimeLimit = 10000
    #model2.Params.NoRelHeurTime = 3600

    model2.optimize()



    optimal_value = "Null"
    if model2.status == gp.GRB.OPTIMAL:
        # Obtener el valor óptimo de la función objetivo
        optimal_value = model2.objVal
        print(optimal_value, end='\t')

    fin2 = time.time()
    tiempo_modelo_arcos = fin2 - inicio2
    print(tiempo_modelo_arcos)

    #model2.reset()

    

    #------------------------------ MODELO BASADO EN CAMINOS
    # 2/julio/2024: ahora implementando el calculo de una cota cuando se trunca la generación de columnas.
    
    inicio1 = time.time()

    num_max_it          = 1900        #número de máximas iteraciones para el modelo (para no saturar gurobi ni el PC).

    (new_paths, 
    dic_cost_path, 
    x_op,
    z_op)              = initial_model(seed,list_comp_FT,K, Travels, Depots, Stations_chrg_time, Stations_chrg_time_dic, Stations_chrg_time_dic_inv, D_v, rs_kt, h, Stations_chrg, dic_comp, cost, list_time, w, fuel, h_inv, dic_comp_F, T_ab, num_max_it, delta, time_window, t, time_dic, delta_mas_i, delta_mas_k, delta_mas_h, Stations_chrg_time_dic_inv_low_res, lowres)

    fin1 = time.time()
    tiempo_modelo_caminos = fin1 - inicio1
    print(tiempo_modelo_caminos, end='\t')

    print(z_op)




