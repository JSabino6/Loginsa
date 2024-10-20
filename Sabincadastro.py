
#completo funcionando

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import os
import time
import names
import random
import zipfile
import threading
import pandas as pd
import requests
import sys
import http.client
import json

print('Caso tenha dúvidas ')
#Lembra de variar o sistema

#API_URL = "studyapi.azure-api.net/"
#ENDPOINT = "/login"

#lembrar de verificar autenticação de token

'''
def login():
    usuario = input("Digite o nome de usuário: ")
    senha = input("Digite a senha: ")
    

    resposta = requests.post('https://zorologi.azurewebsites.net/login', json={"usuario": usuario, "senha": senha})

    if resposta.status_code == 200:
        token = resposta.json().get('token')
        print(f"Login bem-sucedido! Token: {token}")
        return token
    else:
        print("Falha no login. Verifique usuário e senha.")
        sys.exit(1)  

def acessar_area_protegida(token):
    headers = {'Authorization': token}
    resposta = requests.get('https://zorologi.azurewebsites.net/protegido', headers=headers)

    if resposta.status_code == 200:
        print(resposta.json().get('message'))
    else:
        print("Acesso negado!")

if __name__ == "__main__":
    token = login()
    acessar_area_protegida(token)'''



os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0 = INFO, 1 = WARNING, 2 = ERROR
# Autenticação de proxy
def create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass, plugin_path):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version": "22.0.0"
    }
    """

    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{proxy_host}",
                port: parseInt({proxy_port})
            }},
            bypassList: ["localhost"]
        }}
    }};

    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_user}",
                password: "{proxy_pass}"
            }}
        }};
    }}

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );
    """

    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)


# Função para configurar o driver Chrome com proxy
def get_chrome_driver(proxy_host, proxy_port, proxy_user=None, proxy_pass=None):
    plugin_path = 'proxy_auth_plugin.zip'
    
    if proxy_user and proxy_pass:
        create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass, plugin_path)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_extension(plugin_path)
    else:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--proxy-server={proxy_host}:{proxy_port}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


# Função para carregar proxies da planilha Excel
def carregar_proxies_do_excel(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo)
    required_columns = ['host', 'port']
    
    if all(col in df.columns for col in required_columns):
        if 'user' not in df.columns:
            df['user'] = None
        if 'pass' not in df.columns:
            df['pass'] = None
        
        proxies = df.to_dict('records')
        return proxies
    else:
        raise ValueError("A planilha deve conter pelo menos as colunas: host e port")


# Função para carregar CPFs da planilha Excel
def carregar_cpfs_do_excel(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo)
    if 'cpf' in df.columns:
        return df['cpf'].astype(str).tolist()
    else:
        raise ValueError("A planilha deve conter uma coluna chamada 'cpf'")


# Caminhos dos arquivos
caminho_arquivo_proxies = r'C:\Users\joaov\Documents\Python\Dados_proxye.xlsx'
caminho_arquivo_cpfs = r'C:\Users\joaov\Documents\Python\Dados_proxye.xlsx'

# Carregar proxies e CPFs
proxies = carregar_proxies_do_excel(caminho_arquivo_proxies)
cpfs = carregar_cpfs_do_excel(caminho_arquivo_cpfs)


# gerar email e senha
def gerar_email_senha_aleatorio():
    nome_aleatorio = names.get_full_name().replace(" ", "")
    numero_aleatorio = random.randint(100, 999)
    numero_aleatorio_2 = random.randint(0, 9999)
    
    email = f"{nome_aleatorio}{numero_aleatorio}@gmail.com"
    senha = f"{nome_aleatorio}{numero_aleatorio_2}"
    
    return email, senha


#salvar email, senha e proxy em um arquivo txt
def salvar_dados(email, senha, proxy):
    proxy_info = f"{proxy['host']}:{proxy['port']}"
    if proxy['user'] and proxy['pass']:
        proxy_info += f" (user: {proxy['user']}, pass: {proxy['pass']})"
    
    with open('emails_senhas_proxies.txt', 'a') as arquivo:
        arquivo.write(f"Email: {email}, Senha: {senha}, Proxy: {proxy_info}\n")

#alternar as proxys

def get_random_os():
    user_agents = {
        "Windows": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Linux": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
        "Android": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
    }
    os_choice = random.choice(list(user_agents.keys()))
    return user_agents[os_choice], os_choice


def usar_proxy_especifica():
    proxy_input = input("Digite a proxy no formato IP:Port:Username:Password: ").strip()
    proxy_parts = proxy_input.split(":")
    
    if len(proxy_parts) != 4:
        print("Formato de proxy inválido. Certifique-se de usar o formato IP:Port:Username:Password.")
        return
    
    proxy_host, proxy_port, proxy_user, proxy_pass = proxy_parts
    
    #Perguntar se o usuário quer variar o sistema operacional dos navegadores
    variar_os = input("Deseja variar o sistema operacional dos navegadores? (S/N): ").strip().upper()
    
    chrome_options = webdriver.ChromeOptions()

    #variar sistema operacional
    if variar_os == 'S':
        user_agent, os_name = get_random_os()
        chrome_options.add_argument(f"user-agent={user_agent}")
        print(f"Usando navegador com sistema operacional: {os_name}")
    
    #config proxy no navegador
    create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass, "proxy_auth_plugin_especifica.zip")
    chrome_options.add_extension("proxy_auth_plugin_especifica.zip")
    
    #proxy especifica
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(plataforma)

    input('Pressione qualquer tecla para fechar o navegador')
    input('Pressione novamente para confirmar o fechamento')


    print(f"Navegador concluido {proxy_host}:{proxy_port}")
    
    return driver


def gerar_cep():
    url = "https://www.4devs.com.br/ferramentas_online.php"
    data = {
        'acao': 'gerar_cep',
        'estado': '',
        'cidade': '',
        'bairro': '',
        'logradouro': ''
    }

    # Enviar a requisição
    response = requests.post(url, data=data)

    # Verificar o conteúdo da resposta
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            # Tentar extrair os dados relevantes
            cep = soup.find('div', {'id': 'cep'}).text.strip()
            logradouro = soup.find('div', {'id': 'endereco'}).text.strip()
            bairro = soup.find('div', {'id': 'bairro'}).text.strip()
            cidade = soup.find('div', {'id': 'cidade'}).text.strip()
            estado = soup.find('div', {'id': 'estado'}).text.strip()  # Atualize se necessário
            return cep, logradouro, bairro, cidade, estado
        except AttributeError:
            # Caso algum dos elementos não seja encontrado
            print("Erro ao extrair os dados do CEP. Verifique se o site mudou a estrutura.")
            return None, None, None, None, None


def gerar_valor_aleatorio():
    try:
        
        # Verifica se o valor máximo é maior que o mínimo
        if valor_maximo <= valor_minimo:
            print("Erro: O valor máximo deve ser maior que o valor mínimo.")
            return None
        
        # Gera um valor aleatório dentro do intervalo
        valor_aleatorio = random.randint(valor_minimo, valor_maximo)
        print(f"Valor aleatório gerado entre {valor_minimo} e {valor_maximo}: {valor_aleatorio} R$")
        return valor_aleatorio

    except ValueError:
        print("Erro: Por favor, insira números válidos.")
        return None


def separar_nomes(nome_completo):
    partes_nome = nome_completo.split()
    primeiro_nome = partes_nome[0]
    ultimo_nome = partes_nome[-1]
    return primeiro_nome, ultimo_nome






def format_cpf(cpf):
    cpf_clean = re.sub(r'\D', '', cpf)
    if len(cpf_clean) == 11:
        return cpf_clean
    else:
        raise ValueError("CPF inválido. Certifique-se de inserir um CPF com 11 dígitos.")

# Função para obter nome e telefone a partir do CPF
def get_user_data(cpf):
    # Limpa e formata o CPF
    try:
        cpf = format_cpf(cpf)
    except ValueError as e:
        print(e)
        return
    
    # URL com o CPF formatado
    url = f"https://bsp.apibr.in/prod/v1/bigdata/{cpf}"
    
    # Faz a requisição GET
    response = requests.get(url)
    
    # Verifica se o status da resposta é 200 (sucesso)
    if response.status_code == 200:
        data = response.json()

        # Tratamento dos dados para garantir que os campos estejam formatados e limpos
        name = data.get("name", "N/A").title()  # Nome com capitalização correta
        document = data.get("document", "N/A")
        country = data.get("country", "N/A").title()
        gender = data.get("gender", "N/A")
        birthdate = data.get("birthdate", "N/A")
        mother_name = data.get("motherName", "N/A").title()
        father_name = data.get("fatherName", "N/A").title()
        status = data.get("status", "N/A").capitalize()
        document_state = data.get("documentState", "N/A").upper()
        has_obit_indication = "Sim" if data.get("hasObitIndication", False) else "Não"
        age = data.get("age", "N/A")
        email = data.get("email", "N/A")

        # Tratamento dos telefones
        phones = data.get("phones", [])
        if phones:
            main_phone = phones[0]
            phone_code_area = main_phone.get("codeArea", "N/A")
            phone_country = main_phone.get("country", "N/A")
            phone_number = main_phone.get("number", "N/A")
            full_phone = f"{phone_code_area}{phone_number}"
        else:
            full_phone = "N/A"

        # Imprime os dados formatados
        print(f"Nome: {name}")
        print('CPF:', cpf)
        
        return {
            "name": name,
            "phone": full_phone
        }
    else:
        print("Erro na requisição:", response.status_code)
        return None





def carregar_cpfs_do_excel(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo)
    if 'cpf' in df.columns:
        return df['cpf'].astype(str).tolist()
    else:
        raise ValueError("A planilha deve conter uma coluna chamada 'cpf'")

cpfs = carregar_cpfs_do_excel(caminho_arquivo_cpfs)



def selecionar_estado(driver, estado):
    # XPaths para cada estado
    estados_xpath = {
        'AC': "//div[normalize-space()='Acre']",
        'AL': "//div[normalize-space()='Alagoas']",
        'AP': "//div[normalize-space()='Amapá']",
        'AM': "//div[normalize-space()='Amazonas']",
        'BA': "//div[normalize-space()='Bahia']",
        'CE': "//div[normalize-space()='Ceará']",
        'DF': "//div[normalize-space()='Distrito Federal']",
        'ES': "//div[normalize-space()='Espírito Santo']",
        'GO': "//div[normalize-space()='Goiás']",
        'MA': "//div[normalize-space()='Maranhão']",
        'MT': "//div[normalize-space()='Mato Grosso']",
        'MS': "//div[normalize-space()='Mato Grosso do Sul']",
        'MG': "//div[normalize-space()='Minas Gerais']",
        'PA': "//div[normalize-space()='Pará']",
        'PB': "//div[normalize-space()='Paraíba']",
        'PR': "//div[normalize-space()='Paraná']",
        'PE': "//div[normalize-space()='Pernambuco']",
        'PI': "//div[normalize-space()='Piauí']",
        'RJ': "//div[normalize-space()='Rio de Janeiro']",
        'RN': "//div[normalize-space()='Rio Grande do Norte']",
        'RS': "//div[normalize-space()='Rio Grande do Sul']",
        'RO': "//div[normalize-space()='Rondônia']",
        'RR': "//div[normalize-space()='Roraima']",
        'SC': "//div[normalize-space()='Santa Catarina']",
        'SP': "//div[normalize-space()='São Paulo']",
        'SE': "//div[normalize-space()='Sergipe']",
        'TO': "//div[normalize-space()='Tocantins']"
    }


    # Abrir o dropdown do estado
    dropdown_xpath = "//div[contains(@class,'input input-style-1 trigger-input undefined status-invisible false')]//div[contains(@class,'trigger-children')]"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath))).click()

    # Selecionar o estado correspondente
    if estado in estados_xpath:
        estado_xpath = estados_xpath[estado]
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, estado_xpath))).click()
    else:
        print(f"Estado '{estado}' não encontrado no mapeamento.")




print('\n--------------------Use com responsabilidade--------------------\n')
operacao = input('Você deseja realizar registros completos (R), apenas cliques (A), ou abrir um navegador com proxy específica (P)? ').strip().upper()


#plataforma
plataforma = input('Qual site você deseja acessar?\n1- Jon\n2- Blaze\nDigite o valor numérico: ')
if plataforma == '1':
    plataforma = 'https://jonbet.com/'
    print('Digite o valor minimo a ser depositado e o maximo (O sistema irá variar os valores)')
    valor_minimo = int(input("Digite o valor mínimo: "))
    valor_maximo = int(input("Digite o valor máximo: "))
elif plataforma == '2':
    plataforma = 'https://blaze1.space/pt/'
    print('Digite o valor minimo a ser depositado e o maximo (O sistema irá variar os valores)')
    valor_minimo = int(input("Digite o valor mínimo: "))
    valor_maximo = int(input("Digite o valor máximo: "))
else:
    print('Opção inválida. O padrão será Jonbet.')
    print('Digite o valor minimo a ser depositado e o maximo (O sistema irá variar os valores)')
    valor_minimo = int(input("Digite o valor mínimo: "))
    valor_maximo = int(input("Digite o valor máximo: "))
    plataforma = 'https://jonbet.cxclick.com/visit/?bta=63669&brand=jonbet'

if operacao == 'P':
    usar_proxy_especifica()
    input('Pressione espaço para fechar')
    sys.exit(0)

max_navegadores = int(input('Qual o máximo de navegadores que seu PC aguenta simultaneamente? '))

if operacao == 'P':
    usar_proxy_especifica()
    input('Pressione espaço para fechar')
    sys.exit(0)



#navegdor
def acao_navegador(proxy, cpf, primeiro_nome, ultimo_nome, telefone):
    try:
        email_gerado, senha_gerada = gerar_email_senha_aleatorio()
        salvar_dados(email_gerado, senha_gerada, proxy)  # Salvar email, senha e proxy

        driver = get_chrome_driver(proxy["host"], proxy["port"], proxy["user"], proxy["pass"])
        driver.get(plataforma)

        if operacao == 'R':  # Executa registros
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="ACEITAR TODOS OS COOKIES"]'))).click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="header"]/div/div[2]/div/div/div[2]/button'))).click()
            time.sleep(2)
            #Preencher os campos de registro
            driver.find_element(By.XPATH, '//*[@id="auth-modal-register"]/div[2]/form/div[1]/div/input').send_keys(email_gerado)
            time.sleep(1)
            driver.find_element(By.XPATH, '//*[@id="auth-modal-register"]/div[2]/form/div[2]/div/input').send_keys(senha_gerada)
            time.sleep(1)
            cpf_input = driver.find_element(By.XPATH, '//*[@id="auth-modal-register"]/div[2]/form/div[3]/div/div/div/div/input')
            cpf_input.click()
            cpf_input.send_keys(cpf)
            cpf_input.send_keys(Keys.TAB)
            driver.find_element(By.XPATH, '//*[@id="auth-modal-register"]/div[2]/form/div[6]/button').click()
            time.sleep(1)

            #após cadastro porém completo
            #continuar após cadastro (pois pede para selecionar com bonus ou sem)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="bonus-selector"]/button'))).click()
            #driver.find_element(By.XPATH, '//*[@id="bonus-selector"]/button').click()
            time.sleep(1)
            #selecionar o metodo de pagamento (pix)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="method-selector"]/div/div[1]'))).click()
            #driver.find_element(By.XPATH, '//*[@id="method-selector"]/div/div[1]').click()
            #primeiro nome e segundo nome
            driver.find_element(By.XPATH, '//*[@id="new-transaction"]/div/div[2]/div[1]/div/div[2]/div/div/div/input').send_keys(primeiro_nome)
            time.sleep(1)
            driver.find_element(By.XPATH, '//*[@id="new-transaction"]/div/div[2]/div[1]/div/div[3]/div/div/div/input').send_keys(ultimo_nome)
            valor = gerar_valor_aleatorio()
            driver.find_element(By.XPATH, '//*[@id="new-transaction"]/div/div[2]/div[1]/div/div[4]/div/div/div[2]/div[1]/input').send_keys(valor)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="new-transaction"]/div/div[2]/div[2]/div/button[2]'))).click()
            input('Pague o QRcode e *SOMENTE* quando confirmar o pagamento apertar A')

            #Após deposito completo
            time.sleep(3)
            driver.find_element(By.XPATH, '//*[@id="user-info-intermediary"]/div[1]/div/div[1]/div/div/div/div/input').send_keys(primeiro_nome)
            driver.find_element(By.XPATH, '//*[@id="user-info-intermediary"]/div[1]/div/div[2]/div/div/div/div/input').send_keys(ultimo_nome)
            driver.find_element(By.XPATH, '//*[@id="user-info-intermediary"]/div[1]/div/div[3]/div/div/div/input').send_keys(telefone)
            cep, logradouro, bairro, cidade, estado = gerar_cep()
            time.sleep(3)
            driver.find_element(By.XPATH, '//*[@id="user-info-intermediary"]/div[1]/div/div[4]/div/div/div/input').send_keys(logradouro)
            selecionar_estado(driver, estado)
            driver.find_element(By.XPATH, '//*[@id="user-info-intermediary"]/div[1]/div/div[7]/div/div/div/input').send_keys(cidade)
            driver.find_element(By.XPATH, '//*[@id="user-info-intermediary"]/div[1]/div/div[8]/div/div/div/input').send_keys(cep)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="user-info-intermediary"]/div[2]/button'))).click()

            input('A conta foi feita com sucesso, pressione A para concluir')


        
        print(f"Ação concluída com o CPF {cpf} e proxy {proxy['host']} .")
        
    except Exception as e:
        print(f"Erro com o proxy {proxy['host']} e {cpf}")
    finally:
        driver.quit()

#proxies e CPFs em grupos
if operacao == 'R' or operacao == 'A':
    for i in range(0, len(proxies), max_navegadores):
        batch_proxies = proxies[i:i + max_navegadores]
        batch_cpfs = cpfs[i:i + max_navegadores]
        
        threads = []
        for proxy, cpf in zip(batch_proxies, batch_cpfs):
            user_data = get_user_data(cpf)
            if user_data:
                nome_completo = user_data["name"]
                primeiro_nome, ultimo_nome = separar_nomes(nome_completo)
                telefone = user_data["phone"]
            else:
                print(f"Não foi possível obter dados para o CPF {cpf}. ")
            #nome_completo = proxy.get('nome', '')  # Pegue o nome completo da coluna 'nome'
            #primeiro_nome, ultimo_nome = separar_nomes(nome_completo)  # Separe em primeiro e último nome
            
            # Passe as variáveis para a função de ação do navegador
            thread = threading.Thread(target=acao_navegador, args=(proxy, cpf, primeiro_nome, ultimo_nome, telefone))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    print("Processo concluído!")

#abrir navegador especifoco
def get_chrome_driver(proxy_host, proxy_port, proxy_user=None, proxy_pass=None):
    plugin_path = 'proxy_auth_plugin.zip'
    
    if proxy_user and proxy_pass:
        create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass, plugin_path)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_extension(plugin_path)
    else:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--proxy-server={proxy_host}:{proxy_port}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver