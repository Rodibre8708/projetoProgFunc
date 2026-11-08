from collections import namedtuple
from decimal import Context, Decimal, ROUND_HALF_UP
from functools import reduce


# tupla com os campos do csv: facilita leitura e nao altera os dados originais 
Municipio = namedtuple("Municipio", "nome periodo receita dotacao pagas fundeb mde receitas_fundeb receitas_adicionais empenhadas liquidadas")


def numero(texto):
    # converte ex 1.000,00 vira 1000.0
    return Decimal(texto.replace(".", "").replace(",", "."))


def contexto():
    # precisao e arredonda 
    return Context(prec=40, rounding=ROUND_HALF_UP)


def normalizar(linha):
    # cada posição é uma coluna do csv e * separa os valores nos campos
    return Municipio(linha[0].strip(), linha[1].strip(),
                     *map(numero, (linha[2], linha[6], linha[9], linha[10], linha[14],
                                      linha[3], linha[4], linha[7], linha[8])))


def normalizar_dados(linhas):
    # map converte as linhas e tuple guarda o resultado sem permitir alterações
    return tuple(map(normalizar, linhas))


def ranking(registros, campo, maiores=True):
    # campo escolhe receita ou despesa. negativo coloca os maiores primeiro.
    #sorted não muda a ordem original e [:5] pega os cinco primeiros.
    return tuple(sorted(registros, key=lambda r: (-campo(r) if maiores else campo(r), r.nome)))[:5]


def abaixo_de(campo, limite):
    # Devolve a função que o filter vai usar para testar o limite.
    return lambda r: campo(r) < limite


def total_e_media(registros, campo):
    # Usa o campo que foi escolhido para calcular receita ou despesa
    valores = tuple(map(campo, registros))
    # reduce soma os valores começando do zero
    total = reduce(lambda acumulado, valor: contexto().add(acumulado, valor), valores, Decimal(0))
    return total, contexto().divide(total, Decimal(len(valores)))


def buscar_municipio(registros, nome):
    # procura pelo nome igual esta no csv e se nao achar retorna none
    return next(filter(lambda r: r.nome == nome.strip(), registros), None)


def comparar_municipios(primeiro, segundo):
    # cada campo tem uma lambda para pegar o valor correspondente
    campos = (
        ("Receitas de impostos", lambda r: real(r.receita)),
        ("Receitas FUNDEB", lambda r: real(r.receitas_fundeb)),
        ("Receitas adicionais", lambda r: real(r.receitas_adicionais)),
        ("Dotação atualizada", lambda r: real(r.dotacao)),
        ("Despesas empenhadas", lambda r: real(r.empenhadas)),
        ("Despesas liquidadas", lambda r: real(r.liquidadas)),
        ("Despesas pagas", lambda r: real(r.pagas)),
        ("% indicador MDE", lambda r: percentual(r.mde)),
        ("% indicador FUNDEB", lambda r: percentual(r.fundeb)),
    )
    #faz cada linha com o valor dos dois municípios
    return tuple(map(lambda par: (par[0], par[1](primeiro), par[1](segundo)), campos))


def texto_comparacao(primeiro, segundo):
    # a , faz o cabeçalho virar uma tupla com uma linha
    linhas = (("Categorias", primeiro.nome, segundo.nome),) + comparar_municipios(primeiro, segundo)
    # ajusta a largura pra ficar alinhado 
    larguras = tuple(map(lambda i: max(map(lambda linha: len(linha[i]), linhas)), range(3)))
    # zip liga texto e largura, ljust alinha com espaços e join junta as linhas
    return "\n".join(("COMPARAÇÃO MUNICÍPIOS",) + tuple(map( # precisa da virgula depois de COMPARAÇÃO MUNICÍPIOS para juntar o título com a tupla das linhas
        lambda linha: " | ".join(map(lambda par: par[0].ljust(par[1]), zip(linha, larguras))), linhas)))


def formatar_numero(valor):
    # duas casas decimais e forma real
    arredondado = contexto().quantize(valor, Decimal("0.01"))
    return format(arredondado, ",.2f").translate(str.maketrans(",.", ".,"))


def real(valor):
    return "R$ " + formatar_numero(valor)


def percentual(valor):
    return formatar_numero(valor) + "%"


def texto_ranking(registros, campo, titulo, maiores=True):
    return secao(titulo, ranking(registros, campo, maiores=maiores),
                 lambda r: f"{r.nome}: {real(campo(r))}")


def texto_estatisticas(registros, campo, titulo):
    total, media = total_e_media(registros, campo)
    return f"{titulo}\nMunicípios: {len(registros)}\nTotal: {real(total)}\nMédia: {real(media)}"


def texto_filtro(registros, campo, limite, titulo):
    # filter pega os municípios abaixo do limite
    selecionados = tuple(filter(abaixo_de(campo, limite), registros))
    return secao(f"{titulo}: {len(selecionados)}", selecionados,
                 lambda r: f"{r.nome}: {percentual(campo(r))}") 


def secao(titulo, itens, formatador):
    #se o filtro vier vazio mostra que não encontrou municipios
    return "\n".join((titulo,) + tuple(map(formatador, itens))) if itens else titulo + "\nNenhum município."
