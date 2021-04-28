# Camara-Deputados

 Uma pacote simples de integração com a API dos dados abertos da Câmara dos Deputados, com funcionalidades básicas para análises. Esse é um projeto em construção e toda ajuda é bem-vinda! 
 
 A documentação completa da API pode ser encontrada em: https://dadosabertos.camara.leg.br/swagger/api.html

## Funcionalidades

 O pacote funciona tendo como base a função `retirar_dados(onde:String, quem:String, oque:String)`. Essa função acessa é a porta entre o código e a API. Os parâmetros são:
 
 ```
  onde (necessário, padrão=deputados): qual é a localização da informação que você quer.
  quem (opcional): qual o id do item que você quer acessar.
  onde (opcional): qual a informação que você quer.
 ```
As opções de cada um estão presentes na documentação. Um exemplo seria `retirar_dados(onde='deputados', quem='204554', oque='despsas')`. 

O outro pilar do pacote é a classe `Camara`, que define as funções e variáveis básicas de todas as classes, como:
```
 dados:DataFrame = infos gerais dos deputados
 deputados:Dict = {Nome_deputado: Id_deputado}
 partidos:Dict = {Nome_partido: [Nome_deputado_1, Nome_deputado_2, ...]}
 proposicoes:DataFrame = infos da proposicoes
```
Como há muitos dados e pode ser irrelevante iniciar todas essas variáveis com a classe, o valor delas precisa ser atualizado com as funções (exceto do `dados`):
```
 lista_deputados()
 lista_partidos()
 lista_proposicoes(ano:String)
```
As classes podem receber diversos parâmetros de entrada, documentados na API, porém dois mais notáveis são `dataInicio` e `dataFim`, que recebem datas no formato AAAA-MM-DD. 

A classe melhor desenvolvida até agora é a `Deputados`, que tem as informações centrais dos deputados já predefinidas com funções. As funções pré-disponíveis são:
```
 gastos_deputado(id, ano='', plot=False) = retorna um dicionário da seguinte forma {categoria_gastos: valor}.
 gastos_partido(sigla_partido, ano='') = retorna um dicionário com da seguinte forma {nome_deputado: valor_gastos} para os deputados desse partido.
 gastos_partidos(ano='') = retorna dois dicionários da seguinte forma {sigla_partido: valor_total_gasto} e {sigla_partido: valor_total_gasto_por_deputado}.
 deputados_por_partido(ano='') = retorna um dicionário com o nome do partido e o número de deputados por partido ativos no período solicitado.
 proposicoes_deputado(ano='') = atualizada a variável prop_deputado com o nome do deputado e seu número de proposições participantes.
 informacoes(id, ano='') = retorna informações básicas sobre um deputado. 
 escolaridade_partido() = retorna um dicionário composto com o número de deputados, com a respectiva escolaridade, por partido.
 plot_escolaridade(escolaridade_partido) = plota o histograma do dicionário escolaridade_partido.
```


## Exemplo de Uso

 Digamos que você queria saber as escolaridades de cada partido. Para isso basta fazer o seguinte:
 ```
  params = {"dataInicio": "2021-01-01", 'dataFim': '2021-03-31'}
  dep = Deputados(params=params)
  escolaridades = dep.escolaridades_partido()
  dep.plot_escolaridade(escolaridades)
 ```

 E o resultado será:
 ![Escolaridade](https://user-images.githubusercontent.com/77543666/116437112-7b3f4d80-a823-11eb-8354-c3d5cbc50884.png)

 Usando a mesma classe, podemos ver a função `informacoes`. Digamos que sabemos que o deputado Vitor Hugo é o de código 179587, então poderíamos fazer:
 ```
  informacoes('179587')
 ```
 >O deputado sob a id 179587 é VITOR HUGO DE ARAUJO ALMEIDA e faz parte do partido PSL.
 >
 >Seu email é: dep.vitorhugo@camara.leg.br
 >
 >Natural de Salvador, BA, nascido em 1977-05-31.
 >
 >Registrado sob o CPF: 07063842706
 >
 >Escolaridade: Mestrado
 >
 >Despesas no ano 2021 foram: {'MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR': 277977.60000000003}
 >
 >Participa dos órgãos: {'CTASP', 'PLEN', 'PLENARIO', 'PEC39717', 'CD', 'CN', 'CDHM'}
 >
 >O deputado participou de 32 proposições e foi o autor de 15 delas.
 
 Para acessar qualquer dado da API e receber o resultado como uma DataFrame do pandas, basta usar a função `retirar_dados()`:
 ```
  dados = retirar_dados(onde='orgaos')
 ```
 
 Obs: até onde testei, não há limites de requisições por hora, mas posso estar enganado, então cuidado. 
 
 
 
 

