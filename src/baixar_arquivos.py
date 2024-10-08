import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import os
import re
import datetime

""" 
    Baixa o arquivo na pasta de acordo com o diagnóstico do paciente
    
    Params:
    url: link do arquivo a ser baixado
    destino: pasta onde o arquivo será salvo (Healthy ou Sick)
    id_paciente: id do paciente
    descricao_img: descrição da imagem/ posição da foto no corpo do paciente
"""
def baixar_arquivo(url, destino, id_paciente, descricao_img):
    descricao_img = descricao_img.replace(" ", "")
    base_destino = "output/" + destino +"/" + id_paciente + "_img_"+ descricao_img
    endereco_destino = base_destino + ".txt"
    
    #verificar se o arquivo já existe (mais de uma foto por posição)
    contador = 1
    while os.path.exists(endereco_destino):
        endereco_destino = f"{base_destino}_{contador}.txt"
        contador += 1
    
    resposta = requests.get(url, verify=False)
    
    with open(endereco_destino, 'wb') as novo_arquivo:
        novo_arquivo.write(resposta.content)
    print('Download finalizado. Arquivo salvo em: {}'.format(endereco_destino))

""" 
    Extrai ID e diagnóstico do paciente
    Params:
    soup: objeto BeautifulSoup da div que contém a visita em análise
"""
def extrair_diagnostico(soup):
    condition_bs4 = soup.find_all('p', class_='view-diagnostico')
    condition = condition_bs4[0].text
    condition = condition.split(':')[1].strip()
    
    return condition 

"""
    Extrai dados do paciente: ID, Record, Age, Date of registration, Marital status and Race
    Params:
    soup: objeto BeautifulSoup da página 
"""
def extrair_dados_id(soup):
    personal_data = soup.find('div', class_='perfiluser')
    
    #extraindo ID
    id_paciente = personal_data.find('p', class_='titulo2').text.split(':')[1].strip()

    record, age, date_reg, marital_status, race = None, None, None, None, None
    #extraindo informações em 'p'
    description = personal_data.find_all('p')
    for attribute in description:
        if 'Record' in attribute.text:
            record = attribute.text.split(':')[1].strip()
            print(record)
        elif 'years old' in attribute.text:
            pattern = re.compile(r'\d+')
            age = pattern.search(attribute.text).group()
            print(age)
        elif 'Registered' in attribute.text:
            pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
            date_reg = pattern.search(attribute.text).group()
            print(date_reg)
        elif 'Marital status' in attribute.text and 'Race' in attribute.text:
            marital_status = attribute.text.split('.')[0].strip().split(':')[1].strip()
            print(marital_status)
            race = attribute.text.split('.')[1].strip().split(':')[1].strip()
            print(race)
    
    return id_paciente    

"""
    Extrai data das visitas no formato: YYYY-MM-DD
    Params:
    soup: objeto BeautifulSoup da div que contém a data
"""
def extrair_data_visita(soup):
    data = soup.find('label', attrs={'for': 'q2'})
    pattern = re.compile(r'\w+ \d+th, \d{4}')
    data_match = pattern.search(data.text).group()
    
    data_formated = datetime.datetime.strptime(data_match, '%B %dth, %Y').date()
    return data_formated

""" 
    Extrai histórico  do paciente
    Params:
    soup: objeto BeautifulSoup da página, div que contém histórico pessoal (descripctions)
    
"""
#TO DO: completar função para guardar os dados em arquivo
def extrair_personal_data(soup):    
    dado = soup.find_all('p')
    titulo = dado[0].text.strip()
    print(titulo)

    for info in dado[1:]:
        sep_txt = ':' if ':' in info.text else '?'
        data_patient = info.text.replace('-', "").split(sep_txt, 1)
        label = data_patient[0]
        value = data_patient[1] if len(data_patient) > 1 else ""
        print(label)
        print(value)

#TO DO: passar a data para outra função e identificar o diagnóstico da foto
def extrair_data_foto(link):
    pattern = re.compile(r'\w+ \d+th, \d{4}')
    data_match = pattern.search(link).group()

""" 
    Obter os dadsos de cada visita, guardando data e diagnóstico em um map
    Params:
    soup: objeto do BS4 da página
"""
#TO DO: completar a função para guardar os dados em arquivo
def extrair_dados_exames(soup):
    pattern = re.compile(r'exame-termico\d+')
    # Utiliza uma função lambda para verificar se o id da tag corresponde ao padrão regex
    visits = soup.find(lambda tag: tag.name == 'section' and tag.get('id') and pattern.match(tag.get('id')))
    # guardar a data com o diagnostico de cada visita
    visitas_diagnostico = {}
    while visits != None:
        data = extrair_data_visita(visits)
        print(data)
        #completar funcao ->guardar o diagnostico final de acordo com a data do arquivo txt
        diagnostico = extrair_diagnostico(visits)
        print(diagnostico)
        
        visitas_diagnostico[data] = diagnostico
        
        #completar função
        extrair_personal_data(visits.find('div', class_='descripcion1'))
        extrair_personal_data(visits.find('div', class_='descripcion2'))
        extrair_personal_data(visits.find('div', class_='descripcion3'))
        
        visits = visits.find_next(lambda tag: tag.name == 'section' and tag.get('id') and pattern.match(tag.get('id')))

    return visitas_diagnostico

#TO DO: juntar as funções de identificar data da foto e diagnóstico de acordo com as datas das consultas
if __name__ == '__main__':
    
    #acessando página inicial para fazer login
    driver = webdriver.Firefox()
    driver.get("http://visual.ic.uff.br/dmi/")
    username = driver.find_element(By.ID, "usuario")
    password = driver.find_element(By.ID, "password")
    #dados
    username.send_keys("")
    password.send_keys("")
    driver.find_element(By.TAG_NAME, 'button').click()
        
    url = 'http://visual.ic.uff.br/dmi/prontuario/details.php?id=198'
    driver.get(url) 
    
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    
    link_completo = None

    while soup.find('a', class_="right carousel-control") != None:
            #completar função
            id = extrair_dados_id(soup)
            diagnostico = extrair_dados_exames(soup)
            #encontrando as divs com as imagens
            banco_img = soup.find('div', class_='imagenspaciente').find_next('div', class_='imagenspaciente')
            #caso não tenha imagens
            if banco_img != None:
                banco_img = banco_img.find_all('a')
                cont = 0
                for elemento in banco_img:
                    link = elemento.get('href')
                    if link.endswith('.txt'):  # Verifica se o link termina com .txt
                        extrair_data_foto(link)
                        link_completo = urljoin("https://visual.ic.uff.br/dmi/bancovl/", link)  # Constrói o URL completo
                        baixar_arquivo(link_completo, diagnostico, id, str(elemento.get('title')))
                        cont = cont + 1

            #achando o link da proxima pagina
            next_page = soup.find('a', class_="right carousel-control")
            next_page_link = "http://visual.ic.uff.br/dmi/prontuario/" + next_page.get('href')
            driver.get(next_page_link)
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')

    