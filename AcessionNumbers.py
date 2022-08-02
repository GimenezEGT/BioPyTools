from ast import Num


def NumerosDeAcesso():
    arquivo = open(input('Digite o nome do arquivo com extensão: '), "r")
    linhas = arquivo.readlines()
    genbank = list([])

    for linha in linhas:
        if linha.startswith('>'):
            lista = linha.split()
            ac = lista[0].replace('>', '')
            genbank.append(ac)

    with open('NumerosDeAcesso.txt', 'w') as f:
        for i in genbank:
            f.write(i)
            f.write('\n')


NumerosDeAcesso()