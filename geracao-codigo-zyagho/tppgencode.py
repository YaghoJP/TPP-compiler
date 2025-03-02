import sys
import os

from sys import argv, exit

import logging

logging.basicConfig(
     level = logging.DEBUG,
     filename = "gencode.log",
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
from llvmlite import ir
from llvmlite import binding as llvm
error_handler = MyError('GenCodeErrors')

root = None







# Programa Principal.
if __name__ == "__main__":
    if(len(sys.argv) < 2):
        raise TypeError(error_handler.newError('ERR-GC-USE'))

    aux = argv[1].split('.')
    if aux[-1] != 'tpp':
      raise IOError(error_handler.newError('ERR-GC-NOT-TPP'))
    elif not os.path.exists(argv[1]):
        raise IOError(error_handler.newError('ERR-GC-FILE-NOT-EXISTS'))
    else:
        data = open(argv[1])
        source_file = data.read()
        root = parser.parse(source_file)

        if (root):
            pass
        else:
            print(error_handler.newError('WAR-SEM-NOT-GEN-SYN-TREE'))