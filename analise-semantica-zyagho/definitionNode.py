
class NoNumero:
    def __init__(self, valor):
        self.valor = valor


class NoVariavel:
    def __init__(self, tipo, nome, parent=None):
        self.tipo = tipo
        self.nome = nome
        self.parent = parent

class NoOperacaoBinaria:
    def __init__(self, esquerda, operador, direita, nome):
        self.esquerda = esquerda
        self.operador = operador
        self.direita = direita


class NoIdentificador:
    def __init__(self, valor, nome):
        self.valor = valor
        self.name = nome

class NoFuncao:
    def __init__(self, nome, parametros, corpo, retorno):
        self.nome = nome
        self.parametros = parametros,
        self.corpo = corpo
        self.retorno = retorno