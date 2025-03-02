import sys
import os

from sys import argv, exit

import logging

logging.basicConfig(
     level = logging.DEBUG,
     filename = "sema.log",
     filemode = "w",
     format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()


import ply.yacc as yacc
from tppparser import parser
# Get the token map from the lexer.  This is required.
from tpplex import tokens

from mytree import MyNode
from anytree.exporter import DotExporter, UniqueDotExporter
from anytree import RenderTree, AsciiStyle

from myerror import MyError

error_handler = MyError('SemaErrors')



#Declaração das variáveis que serão utilizadas.
root = None
listaErros = []
listaAvisos = []
listaArmazenaNos = []
listaAuxiliarArmazenaNos = []
pilhaEscopo = []

listaArmazenaFuncao = {}
listaArmazenaVariavel = {}


def recuperaEscopo():
    vAux = pilhaEscopo.pop()
    pilhaEscopo.append(vAux)
    return vAux

def adicionaListaVariavelFuncao(id, tipo, escopo, inicializada, declarada, utilizada,inVariavel=True, parametros=None):
    
    if inVariavel:
        listaArmazenaVariavel[id] = {
            "tipo":tipo,
            "escopo":escopo,
            "inicializada":inicializada,
            "declarada":declarada,
            "utilizada":utilizada
        }
        return

    listaArmazenaFuncao[id] = {
        "tipo":tipo,
        "escopo":escopo,
        "inicializada":inicializada,
        "declarada":declarada,
        "utilizada":utilizada,
        "parametros":parametros
        }

def atualizaListaVariavelFuncao(id, escopo,inicializada, utilizada, inVariavel=True):
    vAux = []
    if inVariavel:
        if listaArmazenaVariavel.get(id) is not None:
            vAux = listaArmazenaVariavel[id]
            if vAux["escopo"] == escopo:
                if listaArmazenaVariavel[id]["inicializada"] != True:
                    listaArmazenaVariavel[id]["inicializada"] = inicializada
                if listaArmazenaVariavel[id]["utilizada"] != True:
                    listaArmazenaVariavel[id]["utilizada"] = utilizada
                return
            listaErros.append(f'Erro para o programador: Variavel {id} não identificada')

    if listaArmazenaFuncao.get(id) is not None:
        vAux = listaArmazenaFuncao[id]
        if vAux["escopo"] == escopo:
            if listaArmazenaFuncao[id]["inicializada"] != True:
                listaArmazenaFuncao[id]["inicializada"] = inicializada
            if listaArmazenaFuncao[id]["utilizada"] != True:
                listaArmazenaFuncao[id]["utilizada"] = utilizada

    
def buscaListaVariavelFuncao(id, inVariavel=True):

    if inVariavel:
        return listaArmazenaVariavel.get(id)
    
    return listaArmazenaFuncao.get(id)

#Vai andar na arvore a partir de um nó selecionado.
def caminhaNo(node, inlistaAux=False, listaPropria=None):
    if(len(node.children) >= 1):

        if listaPropria is None:
            if inlistaAux:
                listaAuxiliarArmazenaNos.append(node)
            else:
                listaArmazenaNos.append(node)
        else:
            listaPropria.append(node)

    for i in node.children:
        caminhaNo(i, inlistaAux, listaPropria)

#Valida o todos os nós a partir do declaracao_variavel
def validaDeclaracaoVariaveis(node, inAux=False):

    #percorrendo toda a arvore de declaracao de variaveis e anotando os nós.    
    caminhaNo(node, inAux)

    tipoVariavel = ""
    nomeVariavel = ""
    escopoVariavel = recuperaEscopo()
    listaNos = []
    if inAux:
        listaNos =  listaAuxiliarArmazenaNos
    else:
        listaNos = listaArmazenaNos

    for i in listaNos:
        if i.name == "tipo":
             tipoVariavel = i.children[0].name

        if i.name == "var":
            nomeVariavel = i.children[0].children[0].name

        if i.name == "indice":
            listaIndice = []
            caminhaNo(i,listaPropria=listaIndice)

            for ind in listaIndice:
                if ind.name == "NUM_PONTO_FLUTUANTE":
                    listaErros.append(f"ERR-SEM-ARRAY-INDEX-NOT-INT=Índice de array '{ind.children[0].name}' não 'inteiro'.")
            listaIndice.clear()

    adicionaListaVariavelFuncao(nomeVariavel, tipoVariavel, escopoVariavel, False, True, False)

    if inAux:
        listaAuxiliarArmazenaNos.clear()
    else:
        listaArmazenaNos.clear()

    return

def validaDeclaracaoFuncao(node):

    caminhaNo(node)

    tipoFuncao = ""
    tipoRetorno = ""
    listaParametros = {}
    nomeFuncao = ""
    escopo = recuperaEscopo()

    for i in listaArmazenaNos:
        
        if i.name == "tipo" and i.parent.name == "declaracao_funcao":
            tipoFuncao = i.children[0].name

        if i.name == "ID" and i.parent.name == "cabecalho":
            nomeFuncao = i.children[0].name

        if i.name == "lista_parametros" and i.parent.name == "cabecalho":

            caminhaNo(i, True)

            for j in listaAuxiliarArmazenaNos:
                
                if j.name == "parametro" and j.parent.name == "lista_parametros":
                    tipoParametro = j.children[0].children[0].name
                    nomeParametro = j.children[2].children[0].name
                    if(listaParametros.get(nomeParametro) is None):
                        listaParametros[nomeParametro] = {
                            "tipo":tipoParametro
                        }
                    else:
                        listaErros.append(f"Erro Parametros duplicado {nomeParametro}")
                    
            listaAuxiliarArmazenaNos.clear()

        if i.name == "retorna" and i.parent.name == "acao":
            caminhaNo(i, True)

            for j in listaAuxiliarArmazenaNos:
                
                if j.name == "fator":
                    tipoRetorno = j.children[0].children[0].name


            listaAuxiliarArmazenaNos.clear()

        if i.name == "declaracao_variaveis":
            validaDeclaracaoVariaveis(i, True)

        if i.name == "atribuicao":
            validaAtribuicaoVariaveis(i)
        if i.name == "chamada_funcao":
            validaChamadaFuncao(i, True)

        if i.name == "escreva":
            validaFuncaoEscreva(i, True)

        if i.name == "indice":
            listaIndice = []
            caminhaNo(i,listaPropria=listaIndice)

            for ind in listaIndice:
                if ind.name == "NUM_PONTO_FLUTUANTE":
                    listaErros.append(f"ERR-SEM-ARRAY-INDEX-NOT-INT=Índice de array '{ind.children[0].name}' não 'inteiro'.")
            listaIndice.clear()


    #verificando retorno da funcao
    if ((nomeFuncao == "principal" and tipoRetorno == "") or (nomeFuncao == "principal" and tipoFuncao != "INTEIRO")):
        listaErros.append(f"ERR-SEM-FUNC-RET-TYPE-ERROR: Função '{nomeFuncao}' deveria retornar 'INTEIRO', mas retorna '{tipoRetorno}'.")
    if tipoFuncao == "" and tipoRetorno != "":
        listaErros.append(f"ERR-SEM-FUNC-RET-TYPE-ERROR: Função '{nomeFuncao}' deveria retornar 'Vazio', mas retorna '{tipoRetorno}'.")
    if tipoFuncao == "INTEIRO" and tipoRetorno == "NUM_PONTO_FLUTUANTE":
        listaErros.append(f"ERR-SEM-FUNC-RET-TYPE-ERROR: Função '{nomeFuncao}' deveria retornar '{tipoFuncao}', mas retorna '{tipoRetorno}'.")
    if tipoRetorno == "INTEIRO" and tipoFuncao == "NUM_PONTO_FLUTUANTE":
        listaErros.append(f"ERR-SEM-FUNC-RET-TYPE-ERROR: Função '{nomeFuncao}' deveria retornar '{tipoFuncao}', mas retorna '{tipoRetorno}'.")
    if tipoRetorno == "" and tipoFuncao != "" and nomeFuncao != "principal":
        listaErros.append(f"ERR-SEM-FUNC-RET-TYPE-ERROR: Função '{nomeFuncao}' deveria retornar '{tipoFuncao}', mas retorna 'Vazio'.")


    #armazenando a função na lista de funções
    adicionaListaVariavelFuncao(nomeFuncao, tipoFuncao, escopo, False, True, False, False, listaParametros)

    listaArmazenaNos.clear()
    return

def validaFuncaoEscreva(node, inAux=False):

    caminhaNo(node, inAux)
    tipoFuncao = "VOID"
    tipoRetorno = "VOID"
    idArgumento = ""
    listaParametros = {}

    listaNos = []
    if inAux:
        listaNos =  listaAuxiliarArmazenaNos
    else:
        listaNos = listaArmazenaNos


    for i in listaNos:
        if i.name == "ESCREVA":
            nomeFuncao = i.children[0]
        if i.name == "fator":
            idArgumento = i.children[0].children[0].children[0].name
            idExists = buscaListaVariavelFuncao(idArgumento)
            if idExists is None:
                listaErros.append(f"ERR-SEM-VAR-NOT-DECL=Variável '{idArgumento}' não declarada.")
            else:
                tipoArgumento = idExists["tipo"]
                listaParametros[idArgumento] = {
                    "tipo":tipoArgumento
                }
                atualizaListaVariavelFuncao(idArgumento, recuperaEscopo(), False, True)
    adicionaListaVariavelFuncao(idArgumento, tipoFuncao, recuperaEscopo(), True, True, True, False, listaParametros)
    if inAux:
        listaAuxiliarArmazenaNos.clear()
    else:
        listaArmazenaNos.clear()

def validaVariavelNaoUtilizada():

    for chave, atributos in listaArmazenaVariavel.items():
        if atributos["utilizada"] == False:
            listaAvisos.append(f"WAR-SEM-VAR-DECL-NOT-USED:Variável '{chave}' declarada e não utilizada.")
        if atributos["inicializada"] == False:
            listaAvisos.append(f"WAR-SEM-VAR-DECL-NOT-INIT:Variável '{chave}' declarada e não inicializada.")
    #     for _, atri in var.items():
    #         print(atri["tipo"])

def validaPrincipalExiste():

    for func in listaArmazenaFuncao:
        if func == "principal":
            return True

    listaErros.append("ERR-SEM-MAIN-NOT-DECL:Função 'principal' não declarada.")
    return False

def validaAtribuicaoVariaveis(node):

    caminhaNo(node, True)
    tipoAtribuicao = ""
    idVariavel = ""
    
    for j in listaAuxiliarArmazenaNos:
        if j.name == "ID" and j.parent.name == "var":
            idVariavel = j.children[0].name
            variavelExist = buscaListaVariavelFuncao(idVariavel)
            if variavelExist == None:
                listaErros.append(f"ERR-SEM-VAR-NOT-DECL: Variável '{idVariavel}' não declarada.")
        if j.name == "fator":
            tipoAtribuicao = j.children[0].children[0].name
            if(tipoAtribuicao == "ID"):
                tipoAtribuicao = j.children[0].children[0].children[0].name

            variavel = buscaListaVariavelFuncao(idVariavel)
            if variavel is not None:
                tipoVariavel = variavel["tipo"]
                #print(tipoAtribuicao,tipoVariavel)
                if tipoAtribuicao == "NUM_PONTO_FLUTUANTE" and tipoVariavel != "FLUTUANTE":
                    listaAvisos.append(f"WAR-SEM-ATR-DIFF-TYPES-IMP-COERC-OF-VAR: Atribuição de tipos distintos. Coerção implícita do valor de '{idVariavel}' do tipo '{tipoVariavel}' para '{tipoAtribuicao}'.")
                if tipoAtribuicao == "NUM_INTEIRO" and tipoVariavel != "INTEIRO":
                    listaAvisos.append(f"WAR-SEM-ATR-DIFF-TYPES-IMP-COERC-OF-VAR: Atribuição de tipos distintos. Coerção implícita do valor de '{idVariavel}' do tipo '{tipoVariavel}' para '{tipoAtribuicao}'.")
                
                
                atualizaListaVariavelFuncao(idVariavel, recuperaEscopo(), True, False)
        if j.name == "chamada_funcao":
            listaFuncao = []
            tipoFuncao = []
            validaChamadaFuncao(j, lista=listaFuncao, tipoFuncao=tipoFuncao)

            if variavelExist is not None:
                tipoVariavel = variavelExist.get('tipo', {})
                if tipoFuncao[0] != tipoVariavel:
                    listaAvisos.append(f"WAR-SEM-ATR-DIFF-TYPES-IMP-COERC-OF-VAR: Atribuição de tipos distintos. Coerção implícita do valor de '{idVariavel}' do tipo '{tipoVariavel}' para '{tipoFuncao[0]}'.")
            tipoFuncao.clear()
            
    listaAuxiliarArmazenaNos.clear()

def validaChamadaFuncao(node, inAux=False, lista=None, tipoFuncao=None):

    caminhaNo(node, inAux, lista)

    listaArgumentos = []
    idFuncaoChamada = ""

    listaNos = []
    if inAux:
        listaNos =  listaAuxiliarArmazenaNos
    else:
        listaNos = listaArmazenaNos

    for i in listaNos:

        if i.name == "ID" and i.parent.name == "chamada_funcao":
            idFuncaoChamada = i.children[0].name

        if i.name == "lista_argumentos":
            listaAuxArg = []
            caminhaNo(i, listaPropria=listaAuxArg)

            for t in listaAuxArg:
                if t.name == "fator":
                    varArgumento = t.children[0].children[0].name
                    listaArgumentos.append(varArgumento)
                    if varArgumento != "":
                        atualizaListaVariavelFuncao(varArgumento, recuperaEscopo(), False, True)
            #if(i.children[])
            # varArgumento = i.children[0].children[0].children[0].name
            # if varArgumento == "ID":
            #     varArgumento = i.children[0].children[0].children[0].children[0].name
            # print(varArgumento)
            # listaArgumentos.append(varArgumento)
            
    idExist = buscaListaVariavelFuncao(idFuncaoChamada, False)
    if idExist is not None:
        if tipoFuncao is not None:
            tipoFuncao.append(idExist.get('tipo', {}))
            
        funcaoParametros = idExist.get('parametros', {})
        if len(funcaoParametros) > len(listaArgumentos):
            listaErros.append(f"ERR-SEM-CALL-FUNC-WITH-FEW-ARGS: Chamada à função '{idFuncaoChamada}' com número de parâmetros menor que o declarado.")
            
        if len(funcaoParametros) < len(listaArgumentos):
            listaErros.append(f"ERR-SEM-CALL-FUNC-WITH-MANY-ARGS=Chamada à função '{idFuncaoChamada}' com número de parâmetros maior que o declarado.")

        if len(funcaoParametros) == len(listaArgumentos):
            tiposParametros = [info['tipo'] for info in funcaoParametros.values()]

            contador = 0
            for k in tiposParametros:
                if k == "INTEIRO" and listaArgumentos[contador] != "NUM_INTEIRO":
                    listaAvisos.append(f"WAR-SEM-ATR-DIFF-TYPES-IMP-COERC-OF-FUNC-ARG=Chamada à função '{idFuncaoChamada}' com Coerção implícita do valor do argumento tipo '{listaArgumentos[contador]}' diferente do parâmetro declarado '{k}'.")

                if k == "FLUTUANTE" and listaArgumentos[contador] != "NUM_PONTO_FLUTUANTE":
                    listaAvisos.append(f"WAR-SEM-ATR-DIFF-TYPES-IMP-COERC-OF-FUNC-ARG=Chamada à função '{idFuncaoChamada}' com Coerção implícita do valor do argumento tipo '{listaArgumentos[contador]}' diferente do parâmetro declarado '{k}'.")
                contador = contador + 1
            
    else:
        if idFuncaoChamada == "principal":
            listaErros.append(f"ERR-SEM-CALL-FUNC-MAIN-NOT-ALLOWED: Chamada à função 'principal' não permitida.")
        else:
            listaErros.append(f"ERR-SEM-CALL-FUNC-NOT-DECL: Chamada à função '{idFuncaoChamada}' que não foi declarada.")
    if inAux:
        listaAuxiliarArmazenaNos.clear()
    else:
        listaArmazenaNos.clear()

def andaArvore(node):

    if node.name == "declaracao_variaveis":
        return validaDeclaracaoVariaveis(node)
    
    if node.name == "declaracao_funcao":
        return validaDeclaracaoFuncao(node)

    if(node.name == "atribuicao"):
        return validaAtribuicaoVariaveis(node)

    for i in node.children:
        andaArvore(i)


# Programa Principal.
if __name__ == "__main__":
    if(len(sys.argv) < 2):
        raise TypeError(error_handler.newError('ERR-SEM-USE'))

    aux = argv[1].split('.')
    if aux[-1] != 'tpp':
      raise IOError(error_handler.newError('ERR-SEM-NOT-TPP'))
    elif not os.path.exists(argv[1]):
        raise IOError(error_handler.newError('ERR-SEM-FILE-NOT-EXISTS'))
    else:
        data = open(argv[1])
        source_file = data.read()
        root = parser.parse(source_file)

        if (root):
            pilhaEscopo.append("global")
            andaArvore(root)
            validaVariavelNaoUtilizada()
            validaPrincipalExiste()
            print("Analise semantica realizada.")
            #print(tabela_simbolos)

            for err in listaErros:
                print(err)
            for avi in listaAvisos:
                print(avi)

            print(listaArmazenaVariavel)
            print(listaArmazenaFuncao)
        else:
            print(error_handler.newError('WAR-SEM-NOT-GEN-SYN-TREE'))