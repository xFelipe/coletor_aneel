from urllib.request import urlopen

from bs4 import BeautifulSoup

OUTPUT_FILE_NAME = 'unidades_consumidoras.csv'
ANEEL_BASE_URL = 'http://www2.aneel.gov.br/scg/gd/'
COLUMNS = ('Código da GD', 'Titular da UC', 'Classe', 'Subgrupo',
           'Modalidade', 'Qtde UCs recebem os créditos', 'Município',
           'UF', 'CEP', 'Data Conexão', 'Tipo', 'Fonte',
           'Potência Instalada (kW)', 'Distribuidora')


def format_sublists(page_data, sublist_size):
    """Separa quantidade e formata as linhas do conjunto bruto de dados.

    Itera uma lista maior de strings em sublistas de tamanho `sublist_size`.
    As strings das listas tem os espaços iniciais e finais removidos, e as
    `,` trocadas por `.`.
    """
    if len(page_data) % sublist_size != 0:
        raise ValueError('Tamanho da lista especificada não é divisível pela '
                         'quantidade de colunas({sublist_size}).')
    for i in range(0, len(page_data), sublist_size):
        yield [item.text.strip().replace(',', '.')
               for item in page_data[i:i+sublist_size]]


def get_distrib_data(url):
    """Recebe a url da tabela de distribuidora e retorna as linhas da tabela"""
    with urlopen(url) as page:
        html = page.read()
    bs_page = BeautifulSoup(html.decode('utf-8'), 'html.parser')
    page_data = bs_page.find_all('td', align=('left', 'right'),
                                 class_=None, colspan=None)

    lines = []
    lines.extend(format_sublists(page_data, len(COLUMNS)-1))
    next_page = bs_page.find('a', text='Próxima')
    if next_page:
        lines.extend(get_distrib_data(ANEEL_BASE_URL+next_page['href']))
    return lines


def get_distrib_url(url):
    """Coleta nomes das distribuidoras as urls de suas tabelas"""
    html = urlopen(url)
    bs = BeautifulSoup(html.read().decode('utf-8'), 'html.parser')

    return [(td.a.text, ANEEL_BASE_URL + td.a['href']) for td
            in bs.find_all('td', class_="linhaBranca", align="left")]


def main():
    distrib_urls = get_distrib_url(ANEEL_BASE_URL + 'GD_Distribuidora.asp')

    # print(', '.join(COLUMNS))
    with open(OUTPUT_FILE_NAME, 'w') as output_file:
        output_file.write(', '.join(COLUMNS)+'\n')

    for distrib, url in distrib_urls:
        lines = get_distrib_data(url)
        for line in lines:
            line.append(distrib)
            # print(', '.join(line))
            with open(OUTPUT_FILE_NAME, 'a') as output_file:
                output_file.write(', '.join(line)+'\n')


if __name__ == '__main__':
    main()
