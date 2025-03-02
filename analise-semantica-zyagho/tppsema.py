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


from definitionNode import NoFuncao, NoIdentificador, NoNumero, NoOperacaoBinaria, NoVariavel
error_handler = MyError('SemaErrors')


def validaDeclacaoVariaveis(node, parent=None):
    pass

def criarArvoreAbstrata(nodeArvoreSintatica, parent=None):

    if nodeArvoreSintatica.name == "declaracao_variaveis":
        return validaDeclacaoVariaveis(nodeArvoreSintatica, parent)

    for child in nodeArvoreSintatica.children:
        criarArvoreAbstrata(child, )
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
        arvoreReduzida = MyNode("programa", type="programa")
        if (root):
            AST = MyError()
            arvoreAbstrata = criarArvoreAbstrata(root, arvoreReduzida)
   
            for child in arvoreAbstrata.children:
                print(child.name)
           
            #print_tree(arvoreAbtrata)
            pass
            #print(listaArmazenaFuncao)
            #print(listaArmazenaVariavel)
        else:
            print(error_handler.newError('WAR-SEM-NOT-GEN-SYN-TREE'))