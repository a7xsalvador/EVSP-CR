import gurobipy as gp
import time
import logging


from shortest_paths import shortest_path_with_replenishment 

from lp_functions import calculate_cost, flatten_tuple, from_TDSt_to_V, create_cost_double_apostrophe, create_cost_double_apostrophe_v2

def initial_model(factor_low_res, seed,list_comp_FT, K, Travels, Depots, Stations_chrg_time, Stations_chrg_time_dic, Stations_chrg_time_dic_inv, D_v, rs_kt, h, Stations_chrg, dic_comp, cost, list_time, w, fuel, h_inv, dic_comp_F, T_ab, num_max_it, delta, time_window, t, time_dic, delta_mas_i, delta_mas_k, delta_mas_h, Stations_chrg_time_dic_inv_low_res, lowres):
    '''
    Función para relajación del problema máster y generación de columnas
    02/julio/2024 se incluye el calculo de cotas
    ya no tiene calcuclo de cotas ujuju
    dos modelos activos
    '''
    x_op = {} #guardará la solución cuando sea optima
    optimal_value = None

    num_travels = len(Travels)

    # Crear el objeto del modelo
    model = gp.Model()

    # No outputs
    model.Params.OutputFlag = 0

    # Definir las variables de decisión
    x = {}

    # Se construye los caminos ficticios de costo alto para cada viaje
    new_paths = [[i] for i in Travels]
    M = 1e10 # numero alto
    dic_cost_path = {p:M for p in range(len(new_paths))}

    x = model.addVars(list(dic_cost_path.keys()), vtype=gp.GRB.CONTINUOUS, name='x',obj=dic_cost_path) # el modelo está relajado
    model.ModelSense=gp.GRB.MINIMIZE

    # Primera restricción
    first_restr = model.addConstrs((x[i-1] == 1 for i in Travels), name = '1st_restr')

    # Segunda restriccion 
    second_restr = model.addConstrs(( -gp.quicksum(0*x[i-1] for i in Travels ) >= -D_v[k] for k in Depots), name = '2nd_restr')

    # Tercera restriccion 
    third_restr = model.addConstrs(( -gp.quicksum(0*x[i-1] for i in Travels ) >= -rs_kt[s, t] for (s,t) in Stations_chrg_time), name = '3th_restr')

    model.update()

    #model.write("salidas/modelo_lp.lp")

    # Resolver el modelo
    model.optimize()
    
    # Obtener las variables duales
    alpha_hat = model.getAttr("Pi", first_restr) # viajes
    beta_hat = model.getAttr("Pi", second_restr) # depositos
    gamma_hat = model.getAttr("Pi", third_restr) # estaciones de carga en el tiempo


    # --- Empieza la generación de columnas
    count = 0 # Contador para evitar muchas iteraciones
    count_dic_cost = list(dic_cost_path.keys())[-1] # Da la última llave del diccionario de costos para agregarle nuevos elementos a ese diccionario 
    
    #print(f'ite\tcr<0\tcosto')
# Para evitar que se escriba todo en un solo log
    logger = logging.getLogger()
    # Eliminar handlers existentes
    if logger.hasHandlers():
        logger.handlers.clear()

    logging.basicConfig(filename=f'logs_new/log_cg_{num_travels}_{seed}_{factor_low_res}.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


    time_start_cg = time.time()
    time_spp = 0
    time_spp_low_res = 0
    time_lp = 0
    time_total = 0
    n_cols_low_res = 0

    omega_j = {i:[] for i in Depots}
    min_cost_reduced = {i:[] for i in Depots}
    dic_cost_reduced = {}

    logging.info('\tcount\tz_opt\ttime_spp\ttime_lp\ttime_total\tncols\tnrows\ttime_spp_low_res\tn_cols_low_res')



    while True:
        t_inicio_total = time.time()
        #caa = create_cost_double_apostrophe(alpha_hat, beta_hat, gamma_hat, Travels, h, Depots, cost, h_inv) # caa = c apóstrofe apóstrofe = c''
        # se calcula costos reducidos
        caa = create_cost_double_apostrophe_v2(alpha_hat, beta_hat, gamma_hat, cost, h_inv, delta_mas_i, delta_mas_k, delta_mas_h) 
        num_negative_reduced_cost = 0
        for i in Depots:
            

            # ---- BAJA RESOLUCION 
            t_inicio_spp_low_res = time.time()
            cost_new_path, path = shortest_path_with_replenishment(list_comp_FT, K, Travels, i, caa, h, Stations_chrg_time_dic_inv_low_res, dic_comp, w, fuel, dic_comp_F, T_ab, delta, time_window, t, Depots, time_dic) if lowres == True else (-1,[])
            time_spp_low_res +=  time.time() - t_inicio_spp_low_res

            if cost_new_path >= -0.0001:
                #print(f"el costo es {cost_new_path} en {path}")
                # ---- ALTA RESOLUCION
                t_inicio_spp = time.time()
                cost_new_path, path = shortest_path_with_replenishment(list_comp_FT, K, Travels, i, caa, h, Stations_chrg_time_dic_inv, dic_comp, w, fuel, dic_comp_F, T_ab, delta, time_window, t, Depots, time_dic)
                time_spp +=  time.time() - t_inicio_spp
                if cost_new_path >= -0.0001:
                    #print(f"el costo es {cost_new_path} en {path}")
                    continue
            else:
                n_cols_low_res += 1

                
            num_negative_reduced_cost += 1
            path = flatten_tuple(path)

            path_in_V = from_TDSt_to_V(path, Travels, Depots, Stations_chrg_time_dic, h)
            
            new_paths.append(path_in_V)
            count_dic_cost += 1 # es el contador para indice de los caminos
            dic_cost_path[count_dic_cost] = calculate_cost(path_in_V, cost) # dic_cost_path es el diccionario de costos para el problema máster
            
            omega_j[i].append(count_dic_cost) # se agrega el indice del camino con llave del depósito j. 
            # dic_cost_reduced[count_dic_cost] = cost_new_path
            min_cost_reduced[i] = cost_new_path

            # AGREGAR LA NUEVA COLUMNA AL MODELO
            # crear un objeto columna
            col = gp.Column()


            # Definir los coeficientes de la columna en las restricciones de viajes
            travels_in_path = [i_ for i_ in path_in_V if i_ in Travels]
            for i1 in travels_in_path:
                col.addTerms(1.0, first_restr[i1])
                

            # Definir los coeficientes de la columna en las restricciones de depósitos
            k_ = path_in_V[0]
            col.addTerms(-1.0, second_restr[k_])
   

            # Definir los coeficientes de la columna en las restricciones de capacidad de las estaciones de carga
            ch_t_stations_in_path = [i_ for i_ in path if i_ not in Travels+Depots]
            for i1 in ch_t_stations_in_path:
                col.addTerms(-1.0, third_restr[Stations_chrg_time_dic[i1]])

            # Agregar al programa master reducido una nueva variable asociada a esta columna
            x[count_dic_cost] = model.addVar(name="x[{}]".format(count_dic_cost), vtype=gp.GRB.CONTINUOUS, obj=dic_cost_path[count_dic_cost], column= col)


        model.update()
        count += 1 # Para evitar muchas iteraciones

        if num_negative_reduced_cost>0:
            t_inicio_lp = time.time()
            model.optimize()
            time_lp += time.time() - t_inicio_lp
            alpha_hat = model.getAttr("Pi", first_restr)
            beta_hat = model.getAttr("Pi", second_restr)
            gamma_hat = model.getAttr("Pi", third_restr)
            z_opt = model.objVal
            ncols = model.NumVars
            nrows = model.NumConstrs


  
            #print(f'{z_opt}')
        if count > num_max_it:
            logging.info("\nLLEGÓ AL MAXIMO NUMERO DE ITERACIONES")
            break
        elif num_negative_reduced_cost==0:
            logging.info("\nya no tiene columnas con costo reducido negative")
            break
        time_total += time.time() - t_inicio_total
        logging.info(f'\t{count}\t{z_opt}\t{time_spp}\t{time_lp}\t{time_total}\t{ncols}\t{nrows}\t{time_spp_low_res}\t{n_cols_low_res}')
        
    
    # --- FIN DE LA GENERACIÓN DE COLUMNAS


    # hallar la cota sin pasarlo a binario
    model.Params.OutputFlag = 1
    model.Params.LogFile = f'logs_new/salida_modelo_caminos_{num_travels}_{seed}_{factor_low_res}.log'
    model.Params.TimeLimit = 7200
    
    model.optimize()
    time_finish_cg = time.time() # se registra el tiempo que duró la generación de columnas

    z_continuous = model.objVal # se calcula el z optimo sin aplicar la heurística de pasar a binario (solo con la relajación lineal)
    #print(model.objVal, end="\t")


    # Cambiar el tipo de las variables a binaria y resolver el IP 
    for v in model.getVars():
        v.vtype = gp.GRB.BINARY

    model.optimize()
    z_heuristic = model.objVal # se cambia las variables a binarias y se optimiza

    
    with open(f'logs_new/final_gc_{num_travels}_{factor_low_res}_{seed}.txt', "w") as archivo:
        archivo.write(f'tiempo total\t{time_finish_cg-time_start_cg}\n')
        archivo.write(f'z_continua\t{z_continuous}\n')
        archivo.write(f'z_heuristica\t{z_heuristic}')

    #model.write(f"modelo_lp.lp")

    if model.status == gp.GRB.OPTIMAL:
        # Obtener el valor óptimo de la función objetivo
        optimal_value = model.objVal
        #print('Valor óptimo de la función objetivo:', optimal_value)
        print(optimal_value, end="\t")
        # Obtener la solución óptima de theta
        
        for p in list(dic_cost_path.keys()):
            x_op[p] = x[p].X

    return new_paths, dic_cost_path, x_op, optimal_value
    