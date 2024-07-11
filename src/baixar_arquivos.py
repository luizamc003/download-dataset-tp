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
"""
def extrair_dados_paciente(soup):
    condition_bs4 = soup.find_all('p', class_='view-diagnostico')
    condition = condition_bs4[0].text
    condition = condition.split(':')[1].strip()
    
    id_paciente_bs4 = soup.find('p', class_='titulo2').text
    id_paciente = id_paciente_bs4.split(':')[1].strip()
    
    return condition, id_paciente    

"""
    Extrai dados do paciente: ID, Record, Age, Date of registration, Marital status and Race
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
        
    url = 'http://visual.ic.uff.br/dmi/prontuario/details.php?id=13'
    driver.get(url) 
    
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    
    link_completo = None

    while soup.find('a', class_="right carousel-control") != None:
            #completar função
            diagnostico, id  = extrair_dados_paciente(soup)
            #encontrando as divs com as imagens
            banco_img = soup.find('div', class_='imagenspaciente').find_next('div', class_='imagenspaciente')
            #caso não tenha imagens
            if banco_img != None:
                banco_img = banco_img.find_all('a')
                cont = 0
                for elemento in banco_img:
                    link = elemento.get('href')
                    if link.endswith('.txt'):  # Verifica se o link termina com .txt
                        link_completo = urljoin("https://visual.ic.uff.br/dmi/bancovl/", link)  # Constrói o URL completo
                        baixar_arquivo(link_completo, diagnostico, id, str(elemento.get('title')))
                        cont = cont + 1

            #achando o link da proxima pagina
            next_page = soup.find('a', class_="right carousel-control")
            next_page_link = "http://visual.ic.uff.br/dmi/prontuario/" + next_page.get('href')
            driver.get(next_page_link)
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
    