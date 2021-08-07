from abc import abstractproperty
from django.db.models import constraints, indexes, lookups
from django.shortcuts import render
from django.http import HttpResponse, request 
import folium 
from .models import  cidade, rota 
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from django.views.generic.base import View
from folium import plugins # this line is needed for BeautifyIcon


# Variáveis Globais 
resultado_final = []
valor_distancia = []

data = {}
data['distance_matrix'] = [           
        ]  
data['num_vehicles'] = 1
data['depot'] = 0


class Index(View):
    def get(self,request,id): 
    #Rota Selecionada 
        rota_selecioana = rota.objects.filter(nome_rota= id)   

    # Separar as cidades que precisam ser visitadas 
        cidade_visitadas = [] 
        for i in rota_selecioana:        
            cidade_visitadas.append(i.cidade) 
    
    

    # Abaixo, buscar o ponto de origem 
        tamanho = len(cidade_visitadas)
        cidade1 = ['0']
    
        for i in rota_selecioana: 
            cidades = cidade.objects.filter(cidade_origem=i.cidade)       
            if (i.primeiro == True):
                primeiro1 = i.cidade
           
                for j in cidades:
                    if j.cidade_destino in cidade_visitadas:
                        cidade1.append(j.distancia)
                    

        
    # Inserir o ponto de origem no começo da lista  
        cidade_visitadas = [] 
        for i in rota_selecioana: 
            cidades = cidade.objects.filter(cidade_origem=i.cidade)       
            if (i.primeiro == True):
                cidade_visitadas.append(i.cidade)          
    
    # Inserir os pontos de visitas  
        for i in rota_selecioana: 
            cidades = cidade.objects.filter(cidade_origem=i.cidade)       
            if (i.primeiro == False):
                cidade_visitadas.append(i.cidade)

        

    # Alimenta a tabela interna cidade destino 
        cidade_destino = []
        cidade_des = [] 
        for i in cidade_visitadas:   
            origem = i 
            if len(cidade_destino) != 0:
                cidade_des.append(cidade_destino) 
                cidade_destino = [] 
            for j in cidade_visitadas:
                cidades = cidade.objects.filter(cidade_origem=origem,cidade_destino=j)  
                for j in cidades:            
                    cidade_destino.append(j.distancia)                     
                      
        if len(cidade_destino) != 0:
            cidade_des.append(cidade_destino) 
            cidade_destino = [] 


        # Alimenta a matriz do algoritimo de roteiro 
        data['distance_matrix'].clear() 
        resultado_final.clear()
        valor_distancia.clear()
        for x in cidade_des:
            data['distance_matrix'].append(x)
        
        main() # Executa algoritimo de roteamento
        
        # Ajustando valores que vieram do main()
        texto = ''
        for index, item  in enumerate (resultado_final):
            texto = (item)

        Distancia = [] 
        # Sequencia de cidades a serem visitadas   
        lista_mensagem = texto.split('\n')    
        for index, item  in enumerate (lista_mensagem):
            
            if index ==1: 
                sequencia = item
            if index ==2: 
                Distancia.append(item)
        
        # Define o local do mapa 
        m = folium.Map( location = [-26.358612,-48.8356497], zoon_start=1 )
        
        # Abaixo realiza a lógica de númeração vs cidade ex: 1 - Joinville 
        rotas_seq = []
        sequencia = sequencia.split('->')
        for x in sequencia:
            rotas = rota.objects.filter(nome_rota="sul")
            rotas = rotas.filter( sequecia = x )
            for j in rotas:
                rotas_seq.append(j.cidade)
                
        
        
        soma = 0 
        cidades_feitas = []    
        for x in rotas_seq:    
            cidades1 = cidade.objects.filter(cidade_origem = x )
            for xx in cidades1:
                teste = xx.cidade_origem
                if  teste not in cidades_feitas:
                    
                    folium.Marker(location = [xx.long,xx.lati],
                    icon=folium.plugins.BeautifyIcon(
                              border_color= "Blue",
                              background_color='#FFF',
                              text_color= "Blue",
                              number=soma,
                              icon_shape='marker'),
                              tooltip=soma,
                              popup = xx.cidade_origem
                          ).add_to(m)
                    
                    cidades_feitas.append(xx.cidade_origem)    
                    ultimo  = xx 
                    soma = soma + 1 
                    
        for index,valor in enumerate (cidades_feitas): 
            if index == 0:
                valor_cidade = cidade.objects.filter(cidade_origem = valor)       
                
                
        for x in valor_cidade:       
            folium.Marker(
                location=[ x.long, x.lati ],
                    popup= x.cidade_origem,
                    icon=folium.Icon(icon="cloud"),
                ).add_to(m)      

        
        # Mapa    
        m = m._repr_html_()
        context = {
            'm': m,
            'resultado_final':resultado_final,
            'cidades_feitas' :cidades_feitas,
            'Distancia': Distancia
        }            

        return render(request, 'map.html', context)      
    
    

def create_data_model():
    """Stores the data for the problem."""

    return (data)


def main():
    #"""Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution: #// Descomentar para funcionar
        print_solution(manager, routing, solution)


def print_solution(manager, routing, solution):
    """Prints solution on console."""
    print('Distancia: {} km'.format(solution.ObjectiveValue()))
    valor_distancia.append('Distancia: {} km'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = 'Route for vehicle 0:\n'
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += ' {} ->'.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}\n'.format(manager.IndexToNode(index))
    print(plan_output)
    plan_output += 'Distância percorrida: {}Km\n'.format(route_distance)
    
    resultado_final.append(plan_output)
    



