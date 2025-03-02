[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/RPbIVXl3)
# analise-sintatica-code-start
Este repositório contém o código inicial para o desenvolvimento da fase de __Análise Sintática__.

# Análise Sintática

Análise Sintática determina se a sequência de marcas geradas a partir do código fonte está estruturalmente correta conforme a sintaxe da linguagem. Utilizando para a formalização das regras sintáticas uma Gramática Livre de Contexto (GLC).

A **Análise Sintática** determina a sintaxe ou estrutura de um programa. A sintaxe de uma *LP* é normalmente dada pelas **regras gramaticais** de uma **gramática livre de contexto** (GLC).
Assim como a estrutura léxica é determinada por expressões regulares, uma GLC utiliza convenções para nomes e operações muito similares às usadas por expressões regulares. A diferença é que as regras de uma gramática livre de contexto podem ser **recursivas**.
  	
Existem duas categorias gerais de algoritmos para análise sintática: _Análise Sintática Ascendente_  e _Análise Sintática Descendente_. Escolha que determina como é feita a *análise sintática* e como *árvore sintática* correspondente é construída.

No processo de Análise Sintática o **Analisador Sintático** ou **parser** é responsável por:

+ determinar a estrutura sintática de um programa a partir das **marcas** (tokens) produzidos pelo processo de **varredura** **(scanner, Analisador Léxico)**.
+ construir, explícita ou implicitamente, uma árvore sintática que representa essa estrutura.
+ ao final teremos uma Árvore Sintática construída com as derivações das **regras sintáticas**.

* O analisador sintático é o consumidor da sequências de marcas produzidas pela varredura e gera a árvore sintática.

## Preparação do Ambiente

Como estamos utilizando ferramentas para gerar os _Analisadores Léxico e Sintático_ e na fase final gerarmos o código LLVM-IR na linguagem de programação _Python_, precisamos preparar o ambiente como algumas bibliotecas que serão utilizadas, dentre elas o [PLY](https://www.dabeaz.com/ply/ply.html) -- que gera a implementação da parte léxica e sintática, [AnyTree](https://anytree.readthedocs.io/en/latest) -- para a representação da árvore sintática, o [llvmlite](https://pypi.org/project/llvmlite/) -- para a geração do código LLVM-IR.

__Iremos instalar cada uma das ferramentas:__ [PLY](https://www.dabeaz.com/ply/ply.html), [AnyTree](https://anytree.readthedocs.io/en/latest), [graphviz](https://pypi.org/project/graphviz/) e [llvmlite](https://pypi.org/project/llvmlite/)

Os pré-requisitos podem ser instalados utilizando o arquivo de `requirements.txt`.

```bash
$ pip install  -r requirements.txt
```

```bash
$ cat requirements.txt
pytest
ply
configparser
logging
anytree
graphviz
llvmlite
```

O `PLY` é uma implementação do `lex` e `yacc` para Python. O módulo `ply.yacc` implementa o componente de análise sintática do `PLY`, o nome `yacc` significa _"Yet Another Compiler Compiler"_ e é emprestado da ferramenta Unix.

O `PLY` é implementado inteiramente em `Python` e usa o algoritmo `LR-parsing` o que é razoavelmente eficiente.
* Site: [PLY](https://www.dabeaz.com/ply/) 
* Artigo: [_Prototyping Interpreters using Python Lex-Yacc_ by Shannon Behrens, March 01, 2004](https://www.drdobbs.com/web-development/prototyping-interpreters-using-python-le/184405580)
* [Documentação do PLY](https://www.dabeaz.com/ply/ply.html)
* Github: [PLY 4.0](https://github.com/dabeaz/ply)

Em sua documentação o `PLY` apresenta um exemplo com a implementação de uma  [Calculadora](https://www.dabeaz.com/ply/ply.html#ply_nn24).

Cada regra gramatical é definida por uma função com a especificação da regra em uma _docstring_.

O parâmetro `p` é uma sequência contendo os valores de cada símbolo da gramática na regra correspondente.

Os valores de `p[i]` são mapeados nos símbolos da gramática. O _statement_ `p[0] = p[1] + p[3]` implementa a ação que a regra representa.

```python
def p_expression_plus(p):
    'expression : expression PLUS term'
    #   ^            ^        ^    ^
    #  p[0]         p[1]     p[2] p[3]
    
    p[0] = p[1] + p[3]
```

## Referências

[1] LOUDEN, Kenneth C. **Compiladores:** princípios e práticas. São Paulo, SP: Thomson, c2004. xiv, 569 p. ISBN 8522104220.

[2] AHO, Alfred V. **Compiladores:** princípios, técnicas e ferramentas. 2. ed. São Paulo: Pearson Addison-Wesley, 2008. x, 634 p. ISBN 9788588639249.