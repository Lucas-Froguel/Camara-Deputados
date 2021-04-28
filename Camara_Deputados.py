# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 12:42:38 2021

@author: Lucas
"""
import json
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt

#link: https://dadosabertos.camara.leg.br/api/v2/deputados

def retirar_dados(onde='deputados', quem='', oque='', extras={}):
    '''
        Método para retirar dados da api. 
        Input:
            onde: classe desejada
            quem: id desejada
            oque: categoria desejada
        Output:
            Dataframe com os dados 
        Note que 'oque' e 'quem' são opcionais, mas 'oque' precisa de 'quem'. 
    '''
    link = "https://dadosabertos.camara.leg.br/api/v2/{}".format(onde)
    if quem != '':
        link += "/{}".format(quem)
    if oque != '':
        link += '/{}'.format(oque)
    with requests.get(link, params=extras) as response:
        json_file = response.json()
    return arrumando_dados(pd.json_normalize(json_file))

def arrumando_dados(df):

    df = df.reset_index()

    #print(f"original shape: {df.shape}")
    #print(f"original columns: {df.columns}")


    # search for columns to explode/flatten
    s = (df.applymap(type) == list).all()
    list_columns = s[s].index.tolist()

    s = (df.applymap(type) == dict).all()
    dict_columns = s[s].index.tolist()

    #print(f"lists: {list_columns}, dicts: {dict_columns}")
    while len(list_columns) > 0 or len(dict_columns) > 0:
        new_columns = []

        for col in dict_columns:
            #print(f"flattening: {col}")
            # explode dictionaries horizontally, adding new columns
            horiz_exploded = pd.json_normalize(df[col])
            horiz_exploded.index = df.index
            df = pd.concat([df, horiz_exploded], axis=1).drop(columns=[col])
            new_columns.extend(horiz_exploded.columns) # inplace

        for col in list_columns:
            #print(f"exploding: {col}")
            # explode lists vertically, adding new columns
            df = df.drop(columns=[col]).join(df[col].explode().to_frame())
            new_columns.append(col)

        # check if there are still dict o list fields to flatten
        s = (df[new_columns].applymap(type) == list).all()
        list_columns = s[s].index.tolist()

        s = (df[new_columns].applymap(type) == dict).all()
        dict_columns = s[s].index.tolist()

        #print(f"lists: {list_columns}, dicts: {dict_columns}")

    #print(f"final shape: {df.shape}")
    #print(f"final columns: {df.columns}")
    return df

class Camara:
    def __init__(self, params={}):
        
        self.params = params
        if params == {}:
            self.dados = retirar_dados(onde='deputados')
        else:
            self.dados = retirar_dados(onde='deputados', extras=params)
        self.deputados = {}
        self.partidos = {}
        self.proposicoes = {}
        self.prop_deputado = {}
        
    def lista_deputados(self):
        '''
            Esse método calcula os nomes dos deputados e seus ids e salva na variável 'self.deputados'.
        '''
        for d in set(self.dados['nome']):
            val = list(set(np.where(self.dados['nome'].values==d, self.dados['id'].values, 0)))
            self.deputados[d] = val[1]
    
    def lista_partidos(self):
        '''
            Esse método calcula monta um dicionário da forma {Partido: [deputados_partido]} e
            salva na variável 'self.partidos'
        '''
        for d in set(self.dados['siglaPartido']):
            val = list(set(np.where(self.dados['siglaPartido'] == d, self.dados['nome'], 0)))
            self.partidos[d] = val[1:]
    
    def lista_proposicoes(self, ano=''):
        self.proposicoes = retirar_dados(onde='proposicoes', extras={'ano':ano})

class Deputados(Camara):
    
    def gastos_deputado(self, idd, ano='', plot=False):
        '''
            Essa função recebe o id de um deputado e retorna um dicionário da forma:
                {categoria_gastos: valor}
            Um parâmetro opcional é o 'ano'.
                Ano: string ou lista de strings contendo os anos desejados. Note que ano < dataInicio resultará
                em erro.
        '''
        params = []
        if ano != '':
            params.append(('ano', ano))
        
        data = retirar_dados(onde='deputados', quem=idd, oque='despesas', extras=params)
        if 'tipoDespesa' in data.columns:
            despesas = set(data['tipoDespesa'].values)
            gastos = {}
            for d in despesas:
                gastos[d] = np.sum(np.where(data['tipoDespesa'].values == d, data['valorLiquido'].values, 0))
            
            if plot:
                self.plot_hist(gastos)
        else:
            gastos = {'a': 0}
        return gastos

    def gastos_partido(self, id_partido, ano=''):
        '''
            Método para buscar os gastos de um partido específico.
            Input:
                ano: ano desejado 
            Output:
                gastos: dicionário com o formato {Partido: gastos}
        '''
        if Camara.partidos == {}:
            Camara.lista_partidos()
        if Camara.deputados == {}:
            Camara.lista_deputados()
        
        gasto_total = 0
        for dep in self.partidos[id_partido]:
            dep_id = self.deputados[dep]
            gasto_total += sum(self.gastos_deputado(dep_id, ano=ano).values())
        
        return gasto_total
        
    def gastos_partidos(self, ano=''):
        '''
            Método para calcular os gastos de todos os deputados, classificados por partido.
            Input:
                ano: ano desejado 
            Output:
                gastos: dicionário com o formato {Partido: gastos}
                gastos_deputados: mesmo que 'gastos', mas trocamos o valor bruto gasto por partido 
                                    pelo valor gasto dividido pelo n°deputados do partido (ativos)
        '''
        if self.partidos == {}:
            self.lista_partidos()
        if self.deputados == {}:
            self.lista_deputados()
        
        gastos = {}
        gastos_deputados = {}
        for pt in self.partidos.keys():
            print(pt)
            gastos[pt] = self.gastos_partido(pt, ano=ano)
            gastos_deputados[pt] = gastos[pt] / len(self.partidos[pt])
            
        self.plot_hist(gastos)
        self.plot_hist(gastos_deputados)
        
        return gastos, gastos_deputados
    
    def deputados_por_partido(self, ano=''):
        '''
            Esse método retorna o número de deputados por partido.
            Input:
                ano: ano desejado 
            Output:
                gastos: dicionário com o formato {Partido: n° deputados}
        '''
        if self.partidos == {}:
            self.lista_partidos()
        if self.deputados == {}:
            self.lista_deputados()
        
        deputados = {}
        for pt in self.partidos.keys():
            deputados[pt] = len(self.partidos[pt])
        
        return deputados
        
    def proposicoes_deputado(self, ano=''):
        self.lista_proposicoes(ano=ano)
        
        for prop in set(self.proposicoes['id']):
            de = retirar_dados(onde='proposicoes', quem=prop, oque='autores')['nome']
            for d in de:
                if d in self.prop_deputado.keys():
                    self.prop_deputado[d] += 1
                else:
                    self.prop_deputado[d] = 1
    
    def informacoes(self, idd, ano=''):
        
        data = ano
        if data == '':
            data = '2020'
        
        if self.prop_deputado == {}:
            self.proposicoes_deputado(ano=ano)
        
        dados_dep = retirar_dados(onde='deputados', quem=idd)
        nome = list(dados_dep['dados.ultimoStatus.nome'])[0]
        autorias = retirar_dados(onde='proposicoes', extras={'ano':ano, 'autor': nome})
        
        print('O deputado sob a id {} é {} e faz parte do partido {}.'.format(idd, list(dados_dep.at[0, 'dados.nomeCivil'])[0], list(dados_dep.at[0, 'dados.ultimoStatus.siglaPartido'])[0]))
        print('Seu email é: {}'.format(list(dados_dep.at[0, 'dados.ultimoStatus.email'])[0]))
        print('Natural de {}, {}, nascido em {}.'.format(list(dados_dep.at[0, 'dados.municipioNascimento'])[0], list(dados_dep.at[0, 'dados.ufNascimento'])[0], list(dados_dep.at[0, 'dados.dataNascimento'])[0]))
        print('Registrado sob o CPF: {}'.format(list(dados_dep.at[0, 'dados.cpf'])[0]))
        print('Escolaridade: {}'.format(list(dados_dep.at[0, 'dados.escolaridade'])[0]))
        print('Despesas no ano {} foram: {}'.format(data, self.gastos_deputado(idd, ano=ano)))
        print('Participa dos órgãos: {}'.format(set(retirar_dados(onde='deputados', quem='204554', oque='orgaos')['siglaOrgao'])))
        print('O deputado participou de {} proposições e foi o autor de {} delas.'.format(self.prop_deputado[nome], len(set(autorias['id']))))
        
    def escolaridades_partido(self):
         
        if self.deputados == {}:
            self.lista_deputados()
        if self.partidos == {}:
            self. lista_partidos()
        
        escolaridade_partido = {}
        
        for pt in self.partidos.keys():
            escolaridade = {}
            for dep in self.partidos[pt]:
                dados_dep = retirar_dados(onde='deputados', quem=self.deputados[dep])
                esc = list(dados_dep.at[0, 'dados.escolaridade'])[0]
                if esc in escolaridade.keys():
                    escolaridade[esc] += 1
                else:
                    escolaridade[esc] = 1
            escolaridade_partido[pt] = escolaridade

        
        return escolaridade_partido

    def plot_hist(self, dic, **kwargs):
        fig,ax  = plt.subplots()
            
        ax.bar(dic.keys(), dic.values(), color='b', edgecolor='k', **kwargs)
        fig.autofmt_xdate()
        
    def plot_escolaridade(self, dic, **kwargs):
        df = pd.DataFrame(escolaridades)
        df.transpose.plot.hist(kind='bar', stacked=True, **kwargs)
        
    
#ideia: mapa com as profissoes/escolaridades mais comuns


class Proposicoes(Camara):
    def __init__(self):
        self.prop_deputado = {}
        
    def proposicoes_deputados(self):
        self.lista_proposicoes()
        
        for prop in set(self.proposicoes['id']):
            dep = retirar_dados(onde='proposicoes', quem=prop, oque='autores', extras=self.params).at[:, 'nome']
            for d in dep:
                if d in self.prop_deputado.keys():
                    self.prop_deputado[d] += 1
                else:
                    self.prop_deputado[d] = 1





possibilities = {'deputados':['', 'despesas', 'discursos', 'eventos', 'frentes', 'ocupacoes', 'orgaos', 'profissoes'],
                 'eventos':['', 'deputados', 'orgaos', 'pauta', 'votacoes'], 
                 'frentes':['', 'membros'],
                 'legislaturas':['', 'mesa'], 
                 'partidos':['', 'membros'], 
                 'proposicoes':['', 'autores', 'relacionaos', 'temas', 'tramitacoes', 'votacoes'],
                 'votacoes':['', 'orientacoes', 'votos'],
                 'orgaos':['', 'eventos', 'membros', 'votacoes']
                 }



params = {"dataInicio": "2021-01-01", 'dataFim': '2021-03-31'}

dep = Deputados(params=params)
dep.proposicoes_deputado(ano='2021')
dep.informacoes('179587', ano='2021')

escolaridades = dep.escolaridades_partido()
dep.plot_escolaridade(escolaridades)



