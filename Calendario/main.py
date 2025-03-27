import calendar
from datetime import date, timedelta
from rich.console import Console
from rich.table import Table
from rich.text import Text
import requests
import json

console = Console()

def calcular_pascoa(ano):
    """Calcula a data da Páscoa para um dado ano (algoritmo de Meeus/Jones/Butcher)."""
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)

def listar_feriados(ano):
    """Retorna uma lista de feriados nacionais brasileiros para um dado ano."""
    pascoa = calcular_pascoa(ano)
    carnaval = pascoa - timedelta(days=47)
    sexta_santa = pascoa - timedelta(days=2)
    corpus_christi = pascoa + timedelta(days=60)

    feriados = {
        "01/01": "Confraternização Universal",
        "21/04": "Tiradentes",
        "01/05": "Dia do Trabalho",
        "07/09": "Independência do Brasil",
        "12/10": "Nossa Senhora Aparecida",
        "02/11": "Finados",
        "15/11": "Proclamação da República",
        "25/12": "Natal",
        carnaval.strftime("%d/%m"): "Carnaval",
        sexta_santa.strftime("%d/%m"): "Sexta-feira Santa",
        pascoa.strftime("%d/%m"): "Páscoa",
        corpus_christi.strftime("%d/%m"): "Corpus Christi",
    }
    return feriados

def exibir_calendario(ano, mes=None):
    """Exibe o calendário com feriados e responde dúvidas sobre datas via chatbot."""
    feriados = listar_feriados(ano)
    cal = calendar.Calendar()
    meses = [mes] if mes else range(1, 13)

    for mes_atual in meses:
        tabela = Table(title=f"Calendário {calendar.month_name[mes_atual]} {ano}", show_lines=True)
        legenda_feriados = []
        
        # Adiciona colunas para os dias da semana
        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for dia in dias_semana:
            tabela.add_column(dia, justify="center")
        
        # Monta a tabela do mês
        for semana in cal.monthdayscalendar(ano, mes_atual):
            linha = []
            for dia in semana:
                if dia == 0:
                    linha.append("")  # Dias vazios
                else:
                    data_formatada = f"{dia:02}/{mes_atual:02}"
                    texto = Text(str(dia))
                    if data_formatada in feriados:
                        texto.stylize("bold red")  # Feriados em vermelho
                        legenda_feriados.append(f"{data_formatada}: {feriados[data_formatada]}")
                    linha.append(texto)
            tabela.add_row(*linha)

        # Exibe a tabela do mês
        console.print(tabela)
        
        # Exibe a legenda de feriados do mês
        if legenda_feriados:
            console.print("\n[bold underline]Feriados deste mês:[/]")
            for feriado in legenda_feriados:
                console.print(f"[red]- {feriado}[/]")
        console.print("\n")

    # Exibe a legenda geral
    console.print("\n[bold underline]Legenda Geral:[/]")
    console.print("[red]Vermelho:[/] Feriados")

def responder_duvida(data_perguntada):
    """Função que consulta o modelo de IA para responder a dúvidas sobre datas."""
    prompt = f"O que aconteceu no dia {data_perguntada}?"
    
    url = "http://127.0.0.1:5000"  # URL do modelo Ollama rodando localmente
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "zephyr",  # Ou qualquer modelo que você escolher
        "input": prompt
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        resposta = response.json()
        return resposta["output"]
    else:
        return "Desculpe, não pude encontrar informações para esta data."

def interagir_com_chatbot():
    """Função para interagir com o chatbot no terminal."""
    while True:
        pergunta = input("Pergunte ao chatbot sobre uma data (exemplo: 'O que aconteceu no dia 25/12?') ou digite 'sair' para encerrar: ")
        if pergunta.lower() == 'sair':
            break
        # Extrai a data da pergunta
        # Aqui vamos assumir que a pergunta sempre contém uma data no formato DD/MM
        try:
            data_perguntada = pergunta.split('dia ')[1].split('?')[0]
            resposta = responder_duvida(data_perguntada)
            print(f"Resposta: {resposta}")
        except Exception as e:
            print(f"Não consegui entender a data, tente novamente. Erro: {str(e)}")

# Entrada do usuário
ano = int(input('Digite o ano em formato YYYY: '))
filtrar_mes = input('Deseja filtrar por mês? (S/N): ')

if filtrar_mes.upper() == 'S':
    mes = int(input('Digite o mês em formato MM: '))
    exibir_calendario(ano, mes)
else:
    exibir_calendario(ano)

# Chama o chatbot para responder perguntas
interagir_com_chatbot()
