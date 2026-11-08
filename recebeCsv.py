import csv

def ler_csv(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        next(leitor)  
        # retorna as linhas em tuplas para usar na análise.
        return tuple(map(tuple, leitor))
    
