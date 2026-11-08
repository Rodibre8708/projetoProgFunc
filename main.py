from pathlib import Path
from decimal import Decimal
from parteFuncional import (normalizar_dados, buscar_municipio,
                               texto_comparacao, texto_ranking, texto_estatisticas, texto_filtro)
from recebeCsv import ler_csv


def solicitar_municipio(registros, mensagem):
    while True:
        nome = input(mensagem + " (Enter para cancelar): ")
        if not nome.strip():
            #se der enter sem nada cancela o comando
            return None
        municipio = buscar_municipio(registros, nome)
        if municipio is not None:
            return municipio
        print("Município não encontrado. Digite exatamente igual ao CSV")


def menu_interativo(registros):
    #cada opcao guarda uma função e lamba so faz a consulta quando é chamada 
    opcoes = (
        ("1", "Top 5 maiores receitas de impostos", lambda: texto_ranking(registros, lambda r: r.receita, "TOP 5 - Maiores receitas")),
        ("2", "Top 5 menores receitas de impostos", lambda: texto_ranking(registros, lambda r: r.receita, "TOP 5 - Menores receitas", False)),
        ("3", "Top 5 maiores despesas pagas", lambda: texto_ranking(registros, lambda r: r.pagas, "TOP 5 - Maiores despesas pagas")),
        ("4", "Top 5 menores despesas pagas", lambda: texto_ranking(registros, lambda r: r.pagas, "TOP 5 - Menores despesas pagas", False)),
        ("5", "Total e média das receitas de impostos", lambda: texto_estatisticas(registros, lambda r: r.receita, "Receitas de impostos e transferências")),
        ("6", "Total e média das despesas pagas", lambda: texto_estatisticas(registros, lambda r: r.pagas, "Despesas pagas")),
        ("7", "Municípios com MDE abaixo de 25%", lambda: texto_filtro(registros, lambda r: r.mde, Decimal(25), "MDE abaixo de 25%")),
        ("8", "Municípios com FUNDEB abaixo de 70%", lambda: texto_filtro(registros, lambda r: r.fundeb, Decimal(70), "FUNDEB abaixo de 70%")),
        ("9", "Comparar dois municípios", None),
    )
    # parte da interação do usuario em loop 
    while True:
        print("\nANÁLISE ORÇAMENTÁRIA EDUCAÇÂO PERNAMBUCO 2025 ")
        print("\n".join(map(lambda o: f"{o[0]} - {o[1]}", opcoes)))
        print("0 - Sair")
        escolha = input("Escolha uma opção: ").strip()
        if escolha == "0":
            print("Programa encerrado.")
            return
        opcao = next(filter(lambda o: o[0] == escolha, opcoes), None)
        if opcao is None:
            print("Opção inválida. Escolha um número de 0 a 9.")
        elif escolha == "9":
            # nome 1 e nome 2 para comparção 
            primeiro = solicitar_municipio(registros, "Nome do primeiro município")
            if primeiro is None:
                continue
            segundo = solicitar_municipio(registros, "Nome do segundo município")
            if segundo is None:
                continue
            if primeiro.nome == segundo.nome:
                print("Escolha dois municípios diferentes para comparar.")
                continue
            print("\n" + texto_comparacao(primeiro, segundo))
        else:
            # a posição 2 guarda a função da opção e os parênteses executam essa função
            print("\n" + opcao[2]())


def main():
    # busca o csv na pasta
    caminho = Path(__file__).parent / "SIOPE 2025.csv"
    registros = normalizar_dados(ler_csv(caminho))
    menu_interativo(registros)

#inicia com py main.py 
if __name__ == "__main__":
    main()
