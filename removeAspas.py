# Remove aspas duplas de arquivos .txt, .csv etc

arq = str(input("Digite o caminho para o arquivo: "))
with open (arq, 'r') as entrada, open(arq + ".tmp", 'w+') as saida:
    for line in entrada.readlines():
        print(line)
        saida.write(line.replace('\"',''))