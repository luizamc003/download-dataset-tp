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
    base_destino = "output/" + destino +"/" + str(id_paciente) + "_img_"+ descricao_img
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
    
    dicio_paciente = {}
    
    #extraindo ID
    id_paciente = personal_data.find('p', class_='titulo2').text.split(':')[1].strip()
    dicio_paciente['id'] = id_paciente

    #extraindo informações em 'p'
    description = personal_data.find_all('p')
    for attribute in description:
        if 'Record' in attribute.text:
            record = attribute.text.split(':')[1].strip()
            dicio_paciente['record'] = record
        elif 'years old' in attribute.text:
            pattern = re.compile(r'\d+')
            age = pattern.search(attribute.text).group()
            dicio_paciente['idade'] = age
        elif 'Registered' in attribute.text:
            pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
            date_reg = pattern.search(attribute.text).group()
            dicio_paciente['registro'] = date_reg
        elif 'Marital status' in attribute.text and 'Race' in attribute.text:
            marital_status = attribute.text.split('.')[0].strip().split(':')[1].strip()
            race = attribute.text.split('.')[1].strip().split(':')[1].strip()
            dicio_paciente['estado-civil'] = marital_status
            dicio_paciente['raça'] = race
    
    return dicio_paciente

"""
    Extrai data das visitas no formato: YYYY-MM-DD
    Params:
    soup: objeto BeautifulSoup da div que contém a data
"""
def extrair_data_visita(soup):
    data = soup.find('label', attrs={'for': 'q2'})
    # Atualizado para capturar "st", "nd", "rd", e "th"
    pattern = re.compile(r'(\w+ \d+)(st|nd|rd|th), (\d{4})')
    
    if pattern.search(data.text) == None:
        return 'NA'
    
    data_match = pattern.search(data.text).group()
    print(data_match)
    
    data_match = re.sub(r'(?<=\d)(st|nd|rd|th)', '', data_match)
    print(data_match)
    
    # Converter para datetime e formatar
    data_formated = datetime.datetime.strptime(data_match, '%B %d, %Y').date().isoformat()
    print(data_formated)
    return data_formated

""" 
    Extrai histórico  do paciente
    Params:
    soup: objeto BeautifulSoup da página, div que contém histórico pessoal (descripctions)
    
    return: dicionario de dados do paciente
    
"""
def extrair_personal_data(soup, dic_paciente):
    elementos = soup.find_all(['p', 'span'])  # Encontra todos os elementos <p> e <span>

    for elem in elementos:
        label, value = "", ""
        if elem.name == 'p' and elem.find('span'):  # Se o elemento é um <p> que contém <span>
            info = elem.text.strip().split("?", 1) if "?" in elem.text else elem.text.strip().split(":", 1)
            label = info[0].strip()
            value = info[1].strip() if len(info) > 1 else ""
            continue
        elif elem.name == 'span':  # Se o elemento é um <span>
            label = elem.text.strip()
            value = elem.next_sibling.strip() if elem.next_sibling else ""
        elif elem.name == 'p':
            info = elem.text.strip().split("?", 1) if "?" in elem.text else elem.text.strip().split(":", 1)
            label = info[0].strip()
            value = info[1].strip() if len(info) > 1 else ""

        label = label.replace('-', "").strip().lower() if "-" in label else label.strip().lower()
        value = value.strip().lower() if value != '' else value
        dic_paciente[label] = value
    
""" 
    Extrair diagnóstico de acordo com a data das fotos (no link .txt)
    Params:
    banco: lista de divs com todas as imagens do site, sendo elas .jpg ou .txt
    paciente: dicionário de dados do paciente para extrair o diagnóstico de acordo com a data da foto
"""
def extrair_diagnostico_foto(banco, paciente):
    pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    
    try:    
        for banco_img in banco:
            #caso não tenha imagens
            if banco_img != None:
                link = banco_img.find('a').get('href') if banco_img.find('a') != None else ""
                if link.endswith('.txt'):  # Verifica se o link termina com .txt    
                    
                    data_match = pattern.search(link).group()
                    return paciente[data_match].get('diagnostico')
    except KeyError:
        return "NA"

""" 
    Obter os dadsos de cada visita, guardando data e diagnóstico em um map
    Params:
    soup: objeto do BS4 da página
"""
def extrair_dados_exames(soup):
    #dicionário com as info do id do paciente
    paciente = extrair_dados_id(soup)
    
    pattern = re.compile(r'exame-termico\d+')
    # Utiliza uma função lambda para verificar se o id da tag corresponde ao padrão regex
    visits = soup.find(lambda tag: tag.name == 'section' and tag.get('id') and pattern.match(tag.get('id')))
    
    #vai ser criado outro dicionário dentro do dicio de id para cada visita
    while visits != None:
        #guardar as informações de cada visita
        visitas_diagnostico = {}
        data = extrair_data_visita(visits)
        visitas_diagnostico['diagnostico'] = extrair_diagnostico(visits)
                
        #completar função
        extrair_personal_data(visits.find('div', class_='descripcion1'), visitas_diagnostico)
        extrair_personal_data(visits.find('div', class_='descripcion2'), visitas_diagnostico)
        extrair_personal_data(visits.find('div', class_='descripcion3'), visitas_diagnostico)
        
        paciente[data] = visitas_diagnostico
        
        visits = visits.find_next(lambda tag: tag.name == 'section' and tag.get('id') and pattern.match(tag.get('id')))
    
    return paciente

""" 
    Guardar os dados no csv
    Params:
    pacientes_dic: dicionário de pacientes, cada um com um subdicio de cada visita
"""
def armazenar_dados_csv(pacientes_dic):
    campos_unicos = set(['id', 'record', 'idade', 'registro', 'estado-civil', 'raça'])
    
""" 
    Função para acessar a próxima página
"""
def next_page(soup):
    next_page = soup.find('a', class_="right carousel-control")
    next_page_link = "http://visual.ic.uff.br/dmi/prontuario/" + next_page.get('href')
    driver.get(next_page_link)
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    return soup

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
        
    url = 'http://visual.ic.uff.br/dmi/prontuario/details.php?id=346'
    driver.get(url) 
    
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    
    link_completo = None
    primeira_iteracao = True #variavel de controle
    pacientes_dic = {} #dicionario de dados dos pacientes para colocar no csv
    id_problemas = [] #lista de ids que deram problema
    cont = 0
    

    while soup.find('a', class_="right carousel-control") != None:
            #completar função
            dados_paciente = extrair_dados_exames(soup)
            #encontrando as divs com as imagens
            banco = soup.find_all('div', class_='imagenspaciente')
            if banco == []:
                soup = next_page(soup)
                continue
            
            diagnostico = extrair_diagnostico_foto(banco, dados_paciente)
            
            #problema com diagnóstico
            if diagnostico == 'NA':
                id_problemas.append(dados_paciente['id'])
                soup = next_page(soup)
                continue
                            
            #laço para encontrar a div com os arquivos txt
            for banco_img in banco:
                #caso não tenha imagens
                if banco_img != None:
                    banco_img = banco_img.find_all('a')
                    for elemento in banco_img:
                        link = elemento.get('href')
                        if link.endswith('.txt'):  # Verifica se o link termina com .txt    
                            link_completo = urljoin("https://visual.ic.uff.br/dmi/bancovl/", link)  # Constrói o URL completo
                            baixar_arquivo(link_completo, diagnostico, dados_paciente['id'], str(elemento.get('title')))
            
            print(dados_paciente['id'])
            pacientes_dic[cont] = dados_paciente
            cont += 1
            #achando o link da proxima pagina
            soup = next_page(soup)

    