# Importe o módulo telebot uma vez
import telebot

# Outros imports...
import os
import re
import time
import requests
import html
import io
import json
import threading
import base64
from PIL import Image
from telebot import types


#bot = telebot.TeleBot("5662493800:")
bot = telebot.TeleBot("5998015531:-OwmsQ")

ARQUIVO_JSON = 'grupos.json'

with open(ARQUIVO_JSON, 'r') as arquivo:
    dados_json = json.load(arquivo)

GRUPO = dados_json.get("grupos", [])

PRIVADO = [950764540]
comandos_executados = {}
EXCEPT = [950764540]
ESPERANDO_AUTORIZACAO = {}  # Dicionário para rastrear grupos esperando autorização do dono
DONO_BOT = 950764540

num_groups = len(GRUPO)


mensagem_predefinida = f"""
🆂🅺🆈🅽🅴🆁🅳 🅂🅃🄰🅁🅃
Total de parceiros: {num_groups}

🟢 COMANDO ONLINE
🔴 COMANDO OFFLINE

/menu
/parceiros

🄰🅅🄸🅂🄾 🄸🄼🄿🄾🅁🅃🄰🄽🅃🄴
𝗘𝘀𝘁𝗲 𝗯𝗼𝘁 𝗳𝗼𝗿𝗻𝗲𝗰𝗲 𝗶𝗻𝗳𝗼𝗿𝗺𝗮çõ𝗲𝘀 𝗱𝗶𝘀𝗽𝗼𝗻í𝘃𝗲𝗶𝘀 𝗽𝘂𝗯𝗹𝗶𝗲𝗮𝗺𝗲𝗻𝘁𝗲 𝗲 𝗮𝗽𝗲𝗻𝗮𝘀 𝗽𝗮𝗿𝗮 𝗳𝗶𝗻𝘀 𝗶𝗻𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝘃𝗼𝘀. 𝗖𝗲𝗿𝘁𝗶𝗳𝗶𝗾𝘂𝗲-𝘀𝗲 𝗱𝗲 𝘂𝘀𝗮𝗿 𝗲𝘀𝘀𝗲𝘀 𝗰𝗼𝗺𝗮𝗻𝗱𝗼𝘀 𝗱𝗲 𝗳𝗼𝗿𝗺𝗮 𝗿𝗲𝘀𝗽𝗼𝗻𝘀á𝘃𝗲𝗹 𝗲 𝗲𝗺 𝗰𝗼𝗻𝗳𝗼𝗿𝗺𝗶𝗱𝗮𝗱𝗲 𝗰𝗼𝗺 𝗮 𝗟𝗲𝗶 𝗚𝗲𝗿𝗮𝗹 𝗱𝗲 𝗣𝗿𝗼𝘁𝗲çã𝗼 𝗱𝗲 𝗗𝗮𝗱𝗼𝘀 𝗣𝗲𝘀𝘀𝗼𝗮𝗶𝘀, 𝗟𝗲𝗶 𝗻º 𝟭𝟯.𝟳𝟬𝟵/𝟮𝟬𝟭𝟴.
🄶🅁🅄🄿🄾 🄳🄾 🄱🄾🅃 @divulgafree0
"""

# Função para enviar mensagem a um chat
def enviar_mensagem(chat_id, text):
    bot.send_message(chat_id, text, parse_mode='HTML')

# Figura personalizada
figura_personalizada = """
<pre>
⣿⣿⣿⣿⣿⣿⣿⡿⠛⠛⠋⠉⠙⠻⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⡿⠃⠄⠄⠄⠄⠄⠄⠄⠄⠄⠹⣿⣿⣶⣶⣦⣬⢹⣿
⣿⣿⣿⣿⣿⠄⠄⠄⠄⣰⣧⡀⠄⠄⠄⠄⠈⢙⡋⣿⣿⣿⢸⣿⣿
⣿⣿⣿⣿⣿⠄⠄⠰⠼⢯⣿⣿⣦⣄⠄⠄⠄⠈⢡⣿⣿⣿⢸⣿⣿
⣿⣿⣿⣿⣿⠄⠄⠸⠤⠕⠛⠙⠷⣿⡆⠄⠄⠄⣸⣿⣿⣿⢡⣿⣿
⣿⣿⣿⣿⡇⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⣴⣿⣿⣿⢃⣾⣿⣿
⣿⣿⣿⣿⣇⠄⠄⠄⠄⣄⠄⢀⠄⠄⢀⣤⣾⣿⣿⣿⢃⣾⣿⣿⣿
⣿⠿⣛⣡⣄⣀⠄⠠⢴⣿⣿⡿⣄⣴⣿⣿⣿⣿⣿⢃⣾⣿⣿⣿⣿
</pre>
"""

# Função para verificar se o usuário é um administrador do grupo
def is_user_admin(message):
    user = message.from_user
    chat_id = message.chat.id
    admins = bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user.id for admin in admins)

# Lidar com a adição do bot a novos grupos
@bot.message_handler(content_types=['new_chat_members'])
def on_new_chat_members(message):
    chat_id = message.chat.id

    # Verifique se o bot foi adicionado ao grupo
    for user in message.new_chat_members:
        if user.id == bot.get_me().id:
            if not is_user_admin(message):
                # Se o bot não for um administrador, solicitar a nomeação como administrador
                bot.send_message(chat_id, "Por favor, torne-me um administrador para que eu possa funcionar corretamente neste grupo.")
            else:
                # Se o bot já for um administrador, apresentar-se ao grupo
                bot.send_message(chat_id, figura_personalizada)
                bot.send_message(chat_id, "Olá! Eu sou o seu bot de busca. Você gostaria de me autorizar a funcionar neste grupo? Responda com 'Sim' ou 'Não'.")

# Lidar com as respostas "Sim" ou "Não" dos membros do grupo
@bot.message_handler(func=lambda message: message.text.lower() in ['sim', 'não'])
def handle_permission_response(message):
    chat_id = message.chat.id

    # Verificar se a mensagem é uma resposta "Sim"
    if message.text.lower() == 'sim':
        if chat_id in ESPERANDO_AUTORIZACAO:
            ESPERANDO_AUTORIZACAO.remove(chat_id)  # Remover da lista de espera
            GRUPO.append(chat_id)  # Adicionar o grupo à lista de grupos autorizados
            with open(ARQUIVO_JSON, 'w') as arquivo:
                json.dump({"grupos": GRUPO}, arquivo)
            bot.send_message(chat_id, "Grupo registrado com sucesso! Use /menu para ver os meus comandos.")
        else:
            bot.send_message(chat_id, "Desculpe, não há grupos aguardando autorização.")
    elif message.text.lower() == 'não':
        bot.send_message(chat_id, "Entendi. Não vou mais participar deste grupo. Adeus!")
        bot.leave_chat(chat_id)
def enviar_mensagem_para_grupos():
    while True:
        for grupo_id in GRUPO.copy():
            try:
                chat_info = bot.get_chat(grupo_id)
                if chat_info.type == 'group' or chat_info.type == 'supergroup':
                    bot.send_message(grupo_id, mensagem_predefinida, parse_mode='HTML')
                else:
                    GRUPO.remove(grupo_id)
                    print(f"Grupo {grupo_id} não encontrado e foi removido da lista.")
                    # Remova o grupo do arquivo JSON
                    remover_grupo(grupo_id)
            except telebot.apihelper.ApiException as e:
                if "chat not found" in str(e).lower():
                    print(f"Erro ao enviar mensagem para o grupo {grupo_id}: Chat não encontrado.")
                    # Remova o grupo do arquivo JSON
                    remover_grupo(grupo_id)
                else:
                    print(f"Erro ao enviar mensagem para o grupo {grupo_id}: {str(e)}")
            except Exception as e:
                print(f"Erro ao enviar mensagem para o grupo {grupo_id}: {str(e)}")
        time.sleep(4 * 60 * 60)


def adicionar_grupo(grupo_id):
    if grupo_id not in GRUPO:
        GRUPO.append(grupo_id)
        with open(ARQUIVO_JSON, 'w') as arquivo:
            json.dump({"grupos": GRUPO}, arquivo)
        print(f"Grupo {grupo_id} adicionado ao arquivo JSON.")



@bot.message_handler(commands=['parca'])
def handle_adicionar_grupo(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

   
    if user_id == DONO_BOT:
        if len(message.text.split()) == 2:
            try:
                grupo_id = int(message.text.split()[1])
                adicionar_grupo(grupo_id)
                bot.reply_to(message, f"Grupo {grupo_id} adicionado com sucesso!")
            except ValueError:
                bot.reply_to(message, "Por favor, forneça um ID de grupo válido após o comando.")
        else:
            bot.reply_to(message, "Por favor, use o comando da seguinte forma: /parca idgrupo")

def remover_grupo(grupo_id):
    if grupo_id in GRUPO:
        GRUPO.remove(grupo_id)
        with open(ARQUIVO_JSON, 'w') as arquivo:
            json.dump({"grupos": GRUPO}, arquivo)
        print(f"Grupo {grupo_id} removido do arquivo JSON.")

# Percorra todos os grupos na lista GRUPO
for grupo_id in GRUPO.copy():
    try:
        # Tente enviar uma mensagem para o grupo
        bot.send_message(grupo_id, "Sua mensagem aqui")
    except telebot.apihelper.ApiException as e:
        if "Forbidden" in str(e):
            # O bot não tem permissão para enviar mensagens neste grupo
            print(f"Bot expulso ou não é mais membro do grupo {grupo_id}. Removendo do arquivo JSON.")
            remover_grupo(grupo_id)
        else:
            # Outro erro ocorreu, trate conforme necessário
            print(f"Erro ao enviar mensagem para o grupo {grupo_id}: {str(e)}")




def check_access(chat_id):
    return chat_id in PRIVADO + GRUPO + EXCEPT

def send_html_message(chat_id, text):
    bot.send_message(chat_id, text, parse_mode='HTML')

def show_menu(message):
    if check_access(message.chat.id):
        markup = types.ReplyKeyboardRemove()
        welcome_message = f'<b>BEM VINDO, {message.from_user.first_name}! QUE BOM QUE VOCÊ TEM ACESSO!</b>'

        command_info =  """
🔍 | CONSULTAS DISPONÍVEIS | 🔍

<pre>
🟢 /cpf 02827317508
🟢 /cpf1 02827317508
🟢 /cpf3 02827317508
---
🟢 /cnpj 12345678901234
🟢 /tel 11971995811
🟢 /tel1 63984367346
---
🟢 /foto Fabianna dos Santos Sobreira Ambires
🟢 /nome João da Silva
🟢 /parente João da Silva
---
🔴 /placa ABC1234
🟢 /cep 12345678
🟢 /bin 123456
---
🟢 /ip 204.152.203.157
🟢 /rg 123456789
🟢 /cns 123456789012345
🟢 /titulo 0023404871260
🟢 /ddd 21
</pre>

⚡️ Use os comandos em Grupos e no Privado do Bot!
"""

        send_html_message(message.chat.id, welcome_message)
        send_html_message(message.chat.id, command_info)
    else:
        no_access_message = f'''
        <b>🚀 Ops, @{message.chat.username}! Parece que você ainda não é um membro Premium.</b>

        1. Adicione o bot @minerdbusca_bot ao seu grupo e conceda permissão de administrador.
        2. Digite o comando /getid e pegue o número, que deve ser parecido com isso: -100234245435.
        3. Envie esse número para o tio @batmonn em uma conversa privada e aproveite é gratis! 🚀
        '''

        no_access_info = '<b>Não se preocupe, você não perdeu a festa! 😄 Para desbloquear todos os recursos e comandos exclusivos, torne-se um membro Premium hoje mesmo! Confira todos os comandos disponíveis abaixo:</b>\n\n'

        send_html_message(message.chat.id, no_access_message)
        send_html_message(message.chat.id, no_access_info)



# Função para processar comandos
@bot.message_handler(commands=['start'])
def handle_start(message):
    show_menu(message)

@bot.message_handler(commands=['menu'])
def handle_menu(message):
    show_menu(message)

def adicionar_comando_executado(chat_id, comando):
    if chat_id not in comandos_executados:
        comandos_executados[chat_id] = {}

    if comando not in comandos_executados[chat_id]:
        comandos_executados[chat_id][comando] = 1
    else:
        comandos_executados[chat_id][comando] += 1

def salvar_comandos_em_arquivo():
    for chat_id, comandos in comandos_executados.items():
        if chat_id < 0:
            with open(f'Grupo_{abs(chat_id)}.txt', 'w') as arquivo:
                for comando, vezes_executado in comandos.items():
                    arquivo.write(f'Comando: {comando}\n')
                    arquivo.write(f'Número de Vezes Executado: {vezes_executado}\n')
                    arquivo.write('\n')

# Handler para processar comandos
@bot.message_handler(commands=['cpf3', 'CPF3', 'ddd', 'DDD', 'TITULO', 'titulo', 'CNS', 'RG', 'rg', 'placa', 'PLACA', 'CPF2', 'cpf2', 'cnpj', 'CNPJ', 'ip', 'IP', 'BIN', 'bin', 'cep', 'CEP', 'nome', 'NOME', 'telefone', 'tel', 'tel1', 'telefone1', 'foto', 'cpffree1', 'cpf1', 'CPF1', 'cpffree', 'cpf', 'parente', 'PARENTE'])
def processar_comandos(message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    args = message.text.split(' ')
    comando = args[0]

    print(f"Comando recebido no chat '{chat_title}' ({chat_id}): {comando}")

    # Adicione a busca à lista correspondente ao grupo
    adicionar_comando_executado(chat_id, comando)

    if check_access(chat_id):
        if comando in ['/nome', '/NOME']:
            consultar_nome(message, args)
        elif comando in ['/telefone', '/tel']:
            consultar_telefone(message, args)
        elif comando in ['/telefone1', '/tel1']:
            consultar_telefone1(message, args)
        elif comando == '/foto':
            consultar_foto(message, args)
        elif comando in ['/cpffree1', '/cpf1']:
            consultar_cpffree1(message, args)
        elif comando in ['/cpffree', '/cpf']:
              consultar_cpffree(message, args)
        elif comando in ['/cep', '/CEP']:
            consultar_cep(message, args)
        elif comando in ['/cnpj', '/CNPJ']:
            consultar_cnpj(message, args)
        elif comando in ['/bin', '/BIN']:
            consultar_bin(message, bot)
        elif comando in ['/ip', '/IP']:
            consultar_ip(message, args)
        elif comando in ['/rg', '/RG']:
            consultar_rg(message, args)
        elif comando in ['/titulo', '/TITULO']:
            consultar_titulo(message, args)
        elif comando in ['/CNS', '/cns']:
            consultar_cns(message, args)
        elif comando in ['/ddd', '/DDD']:
            consultar_ddd(message, args)
        elif comando in ['/cpf3', '/CPF3']:
            consultar_cpf3(bot, message, args)
        elif comando in ['/parente','/PARENTE']:
            consultar_parente(message, args)
            
        salvar_comandos_em_arquivo()

# Função para consultar CPF
def consultar_cpf3(bot, message, args):
    chat_id = message.chat.id

    if len(args) != 2:
        bot.send_message(chat_id, "Por favor, forneça o CPF para consultar os parentes.")
        return

    cpf = args[1]

    try:
        # Realizar uma solicitação GET para a nova API com o CPF
        response = requests.get(f"http://api3.minerdxc.tk:8080/api/cpf1?cpf={cpf}")
        data = response.json()

        if data:
            resultado_consulta = "Dados do CPF:\n\n"
            
            for key, value in data.items():
                if value is not None and value != "":
                    resultado_consulta += f"*{key}*: `{value}`\n"

            # Enviar a resposta pelo bot
            bot.send_message(chat_id, resultado_consulta, parse_mode='Markdown')
        else:
            bot.send_message(chat_id, "⚠ CPF não encontrado.")
    except Exception as error:
        print(f"Erro ao consultar CPF: {str(error)}")
        bot.send_message(chat_id, "⚠ Ocorreu um erro ao consultar o CPF.")

def consultar_parente(message, args):
    chat_id = message.chat.id

    if len(args) != 2:
        bot.send_message(chat_id, "Por favor, forneça o CPF para consultar os parentes.")
        return

    cpf = args[1]

    try:
        # Realizar uma solicitação GET para a API de parentes com o CPF
        response = requests.get(f"http://api3.minerdxc.tk:8080/api/parente?cpf={cpf}")
        parente_data = response.json()

        if parente_data:
            resultado_consulta = f"**Parentes associados ao CPF {cpf}:**\n\n"
            for parente in parente_data:
                nome_parente = parente.get("NOME_VINCULO", "Desconhecido")
                vinculo = parente.get("VINCULO", "Desconhecido")
                resultado_consulta += f"Nome do Parente: {nome_parente}\nVínculo: {vinculo}\n\n"

            # Envie a resposta pelo bot
            bot.send_message(message.chat.id, resultado_consulta, parse_mode='Markdown')
        else:
            # Envie a resposta pelo bot
            bot.send_message(message.chat.id, "⚠ Nenhum parente encontrado para este CPF.")
    except Exception as error:
        print(f"Erro ao consultar parentes: {str(error)}")
        # Envie a resposta pelo bot
        bot.send_message(message.chat.id, "⚠ Ocorreu um erro ao consultar os parentes.")


@bot.message_handler(commands=['getid'])
def handle_getid(message):
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        bot.send_message(message.chat.id, f'O ID deste grupo é: {message.chat.id}')
        if message.chat.id == 950764540:
            # Se o comando foi dado no grupo com ID 950764540, envie uma mensagem para o usuário com o mesmo ID
            bot.send_message(950764540, 'Alguém pediu o ID do grupo.')



@bot.message_handler(commands=['parceiros'])
def listar_grupos_parceiros(message):
    chat_id = message.chat.id
    response = "Grupos registrados como parceiros:\n\n"
   
    for grupo_id in GRUPO:
        try:
            chat_info = bot.get_chat(grupo_id)
            title = chat_info.title
            invite_link = chat_info.invite_link  # Obtém o link de convite (se disponível)
            if invite_link:
                response += f"- <a href='{invite_link}'>{title}</a>\n"
            else:
                response += f"- {title}\n\n"
        except Exception as e:
            response += f"- Grupo Privado {grupo_id}\n\n"

    bot.send_message(chat_id, response, parse_mode='HTML')







def consultar_ddd(message, args):
    chat_id = message.chat.id
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    if len(args) < 2:
        bot.reply_to(message, 'Inserir ddd com apenas 2 digitos')
        return

    ddd = args[1]

    try:
        response = requests.get(f'https://brasilapi.com.br/api/ddd/v1/{ddd}')
        ddd_data = response.json()

        if 'state' in ddd_data and 'cities' in ddd_data:
            state = ddd_data['state']
            cities = ddd_data['cities']

            dddlist = f'Lista de Cidades de {state} com este DDD {ddd}:\n\n'
            for i, city in enumerate(cities, 1):
                dddlist += f'{i} ⪧ {city}\n'

            bot.send_message(chat_id, dddlist)

        else:
            bot.reply_to(message, 'Dados de DDD não encontrados.')

    except Exception as e:
        bot.reply_to(message, 'Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.')





def consultar_cns(message, args):
    chat_id = message.chat.id
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    if len(args) < 2:
        bot.reply_to(message, 'Por favor, forneça o número do CNS para consulta.')
        return

    cns = args[1]

    # Sua URL de consulta de CNS
    url = f'http://api2.minerdxc.tk:8080/api/cns?cns={cns}'

    try:
        # Faça a solicitação à API
        response = requests.get(url)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 200:
            formatted_result = []

            # Tente analisar a resposta como JSON, considerando a estrutura list[dict]
            try:
                data = response.json()

                # Itere pelas listas e dicionários aninhados para obter os pares key: value
                for sublist in data:
                    for subdict in sublist:
                        for key, value in subdict.items():
                            formatted_result.append(f"{key}: {value}")

            except ValueError:
                # Se a resposta não puder ser analisada como JSON, trate-a como texto
                formatted_result.append(response.text)

            # Crie a mensagem de resposta
            resposta = '\n'.join(formatted_result)

            # Envie a mensagem ao usuário
            bot.send_message(chat_id, resposta, parse_mode='HTML')

        else:
            bot.reply_to(message, 'Não foi possível consultar o CNS neste momento. Tente novamente mais tarde.')

    except Exception as e:
        bot.reply_to(message, 'Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.')



def consultar_titulo(message, args):
    chat_id = message.chat.id
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')

    if len(args) < 2:
        bot.reply_to(message, 'Por favor, forneça o número do título para consulta.')
        return

    titulo = args[1]

    # Sua URL de consulta de título
    url = f'http://api2.minerdxc.tk:8080/api/titulo?titulo={titulo}'

    try:
        # Faça a solicitação à API
        response = requests.get(url)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 200:
            formatted_result = []

            # Tente analisar a resposta como JSON, considerando a estrutura list[dict]
            try:
                data = response.json()

                # Itere pelas listas e dicionários aninhados para obter os pares key: value
                for sublist in data:
                    for subdict in sublist:
                        for key, value in subdict.items():
                            formatted_result.append(f"{key}: {value}")

            except ValueError:
                # Se a resposta não puder ser analisada como JSON, trate-a como texto
                formatted_result.append(response.text)

            # Crie a mensagem de resposta
            resposta = '\n'.join(formatted_result)

            # Envie a mensagem ao usuário
            bot.send_message(chat_id, resposta, parse_mode='HTML')

        else:
            bot.reply_to(message, 'Não foi possível consultar o título neste momento. Tente novamente mais tarde.')

    except Exception as e:
        bot.reply_to(message, 'Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.')




def consultar_rg(message, args):
    chat_id = message.chat.id
    liberado_nome = PRIVADO + GRUPO + EXCEPT
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    if chat_id not in liberado_nome:
        bot.reply_to(message, 'Você não tem permissão para usar este comando neste chat.')
        return

    if len(args) < 2:
        bot.reply_to(message, 'Por favor, forneça o número do RG para consulta.')
        return

    rg = args[1]

    # Sua URL de consulta de RG
    url = f'http://api2.minerdxc.tk:8080/api/rg?rg={rg}'

    try:
        # Faça a solicitação à API
        response = requests.get(url)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 200:
            formatted_result = []

            # Tente analisar a resposta como JSON, considerando a estrutura list[dict]
            try:
                data = response.json()

                # Itere pelas listas e dicionários aninhados para obter os pares key: value
                for sublist in data:
                    for subdict in sublist:
                        for key, value in subdict.items():
                            formatted_result.append(f"{key}: {value}")

            except ValueError:
                # Se a resposta não puder ser analisada como JSON, trate-a como texto
                formatted_result.append(response.text)

            # Crie a mensagem de resposta
            resposta = '\n'.join(formatted_result)

            # Envie a mensagem ao usuário
            bot.send_message(chat_id, resposta, parse_mode='HTML')

        else:
            bot.reply_to(message, 'Não foi possível consultar o RG neste momento. Tente novamente mais tarde.')

    except Exception as e:
        bot.reply_to(message, 'Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.')


def consultar_telefone(message, args):
    chat_id = message.chat.id
    liberado_nome = PRIVADO + GRUPO + EXCEPT
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    if chat_id in liberado_nome:
        if len(args) < 2:
            bot.send_message(
                chat_id,
                'Por favor, forneça um número de telefone após o comando /telefone.'
            )
            return

        bot.send_message(
            chat_id,
            'Aguarde, esta consulta pode demorar...'
        )

        telef = args[1]

        if not telef.isdigit():
            bot.send_message(
                chat_id,
                "❌ Telefone inválido. Por favor, insira apenas números (sem espaços ou caracteres especiais)."
            )
            return

        if len(telef) < 10 or len(telef) > 11:
            bot.send_message(
                chat_id,
                "❌ Telefone inválido. Por favor, insira um número de telefone com 10 ou 11 dígitos."
            )
            return

        try:
            start_time = time.time()

            response = requests.get(
                f'http://api2.minerdxc.tk:8080/api/telefones2?telefone={telef}'
            )

            end_time = time.time()
            elapsed_time = end_time - start_time

            data = response.json()

            if "data" in data:
                formatted_result = []
                for table_name, table_data in data["data"].items():
                    for item in table_data:
                        for key, value in item.items():
                            formatted_result.append(f"{key}: {value}")

                formatted_result.append(f"Tempo de resposta da API: {elapsed_time:.2f} segundos")

                bot.send_message(
                    chat_id,
                    '\n'.join(formatted_result)
                )

            else:
                bot.send_message(
                    chat_id,
                    '❌ DADOS NAO ENCONTRAOS'
                )

        except Exception as e:
            print("❌ Erro ao consultar telefone:", str(e))
            bot.send_message(
                chat_id,
                "❌ Ocorreu um erro ao consultar o telefone. Por favor, tente novamente mais tarde."
            )


def formatar_resposta_api(data):
    formatted_result = []

    if "data" in data:
        for table_name, table_data in data["data"].items():
            for item in table_data:
                for key, value in item.items():
                    formatted_result.append(f"{key}: {value}")

    return formatted_result





def consultar_cpffree1(message, args):
    try:
        bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
        if len(args) < 2:
            bot.reply_to(message, 'Por favor, forneça um número de CPF após o comando /cpffree1.')
            return

        cpf_comando = args[1]

        if not cpf_comando.isdigit() or len(cpf_comando) != 11:
            bot.reply_to(message, "❌ CPF inválido. Por favor, insira um CPF válido com exatamente 11 dígitos numéricos, sem caracteres especiais ou espaços.")
            return

        url = f'http://api2.minerdxc.tk:8080/api/cpf6?cpf={cpf_comando}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if "data" in data:
                result_data = data["data"]
                formatted_result = []
                unique_fields = set()  # Conjunto para armazenar campos únicos

                for table_name, table_data in result_data.items():
                    for item in table_data:
                        for key, value in item.items():
                            if key not in unique_fields:
                                formatted_result.append(f"{key}: {value}")
                                unique_fields.add(key)

                # Envia o resultado como mensagem formatada em HTML
                bot.send_message(message.chat.id, '\n'.join(formatted_result), parse_mode='HTML')


            else:
                bot.reply_to(message, '❌ DADOS NAO ENCONTRADOS.')

        else:
            bot.reply_to(message, '❌ Ocorreu um erro ao consultar o CPF. Verifique se o CPF é válido e tente novamente.')

    except Exception as e:
        print("Erro ao consultar CPF:", str(e))
        bot.reply_to(message, '❌ Ocorreu um erro ao consultar o CPF.')

def consultar_cnpj(message, args):
    liberadocnpj = PRIVADO + GRUPO + EXCEPT
    chat_id = message.chat.id
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    if chat_id in liberadocnpj:
        if len(args) < 2:
            bot.reply_to(message, '<b>DIGITE UM CNPJ, ANIMAL!</b>', parse_mode='HTML')
        else:
            try:
                cnpj = re.sub('[^0-9]', '', args[1])
                url = f'https://hyb.com.br/curl_cnpj.php?action=acessa_curl&cnpj={cnpj}'
                response = requests.get(url)
                data = response.json()

                if 'cnpj' in data:
                    razao_social = data.get('razao_social', 'N/A')
                    nome_fantasia = data.get('nome_fantasia', 'N/A')
                    situacao = data.get('situacao', 'N/A')
                    cnae = data.get('cnae_fiscal', 'N/A')
                    telefone = data.get('telefone_1', 'N/A')
                    email = data.get('email', 'N/A')
                    resposta =  '▱▱▱▱▱▱▱▱▱▱▱▱▱\n'
                    resposta = f"<b>Informações do CNPJ {cnpj}:</b>\n\n"
                    resposta += f"<b>Razão Social:</b> {razao_social}\n"
                    resposta += f"<b>Nome Fantasia:</b> {nome_fantasia}\n"
                    resposta += f"<b>Situação:</b> {situacao}\n"
                    resposta += f"<b>CNAE Fiscal:</b> {cnae}\n"
                    resposta += f"<b>Telefone:</b> {telefone}\n"
                    resposta += f"<b>Email:</b> {email}\n"
                    resposta =  '▱▱▱▱▱▱▱▱▱▱▱▱▱\n'
                    bot.reply_to(message, resposta, parse_mode='HTML')
                    adicionar_comando_executado(chat_id, cnpj, message.text, resposta)

                else:
                    bot.reply_to(message, '<b>CNPJ NÃO ENCONTRADO</b>', parse_mode='HTML')
            except:
                bot.reply_to(message, '<b>CNPJ NÃO ENCONTRADO</b>', parse_mode='HTML')
    else:
        bot.reply_to(message, '<b>Você não tem autorização para utilizar esse comando! Seja um usuário VIP, ganhe benefícios e tenha acesso a todas as Consultas, 24h por dia. @@batmonn</b>', parse_mode='HTML')


def consultar_ip(message, args):
    liberadoip = PRIVADO + GRUPO + EXCEPT
    chat_id = message.chat.id
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    if chat_id in liberadoip:
        if len(args) < 2:
            bot.reply_to(message, '<b>DIGITE UM IP, ANIMAL!</b>', parse_mode='HTML')
        else:
            try:
                ip = re.sub('[^0-9.]', '', args[1])
                url = requests.get(f'http://ip-api.com/json/{ip}')
                req = url.json()
                bot.reply_to(message,
                             f'▱▱▱▱▱▱▱▱▱▱▱▱▱\n'
                             f'𝙄𝙋: {req.get("query", "")}\n'
                             f'𝙋𝘼𝙄́𝙎: {req.get("country", "")}\n'
                             f'𝙎𝙄𝙂𝙋𝘼 𝙋𝘼𝙄́𝙎: {req.get("countryCode", "")}\n'
                             f'𝙍𝙀𝙂𝙄𝘼̃𝙊: {req.get("region", "")}\n'
                             f'𝙍𝙀𝙂𝙄𝘼̃𝙊 𝙉𝘼𝙈𝙀: {req.get("regionName", "")}\n'
                             f'𝘾𝙄𝘿𝘼𝘿𝙀: {req.get("city", "")}\n'
                             f'𝘾𝙀𝙋: {req.get("zip", "")}\n'
                             f'𝙇𝘼𝙏𝙄𝙏𝙐𝘿𝙀: {req.get("lat", "")}\n'
                             f'𝙇𝙊𝙉𝙂𝙄𝙏𝙐𝘿𝙀: {req.get("lon", "")}\n'
                             f'𝙋𝙍𝙊𝙑𝙀𝘿𝙊𝙍: {req.get("org", "")}\n'
                            f'▱▱▱▱▱▱▱▱▱▱▱▱▱\n'
                             '𝙂𝙍𝙐𝙋𝙊:  @minerdgrupo', parse_mode='HTML')
            except:
                bot.reply_to(message, '<b>IP NÃO ENCONTRADO</b>', parse_mode='HTML')
    else:
        bot.reply_to(message, '<b>Você não tem autorização para utilizar esse comando! Seja um usuário VIP, ganhe benefícios e tenha acesso a todas as Consultas, 24h por dia. @@batmonn</b>', parse_mode='HTML')


def consultar_bin(message, bot):
    notbin = []
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    bid = message.chat.id
    cp = message.text
    if bid in notbin:
        bot.reply_to(message, '⚠️ Você está na lista de exclusão para consulta de BIN! ⚠️')
    else:
        try:
            bn = re.sub('[^0-9]', '', cp)
            response = requests.get(f'https://lookup.binlist.net/{bn}')
            res = response.json()

            if "error" not in res:
                bin_code = res.get("bin", "")
                brand = res.get("brand", "")
                card_type = res.get("type", "")
                category = res.get("category", "")
                bank_name = res.get("bank", {}).get("name", "")
                bank_phone = res.get("bank", {}).get("phone", "")
                bank_url = res.get("bank", {}).get("url", "")
                country_name = res.get("country", {}).get("name", "")
                country_alpha3 = res.get("country", {}).get("alpha3", "")
                country_alpha2 = res.get("country", {}).get("alpha2", "")

                resposta = f'▱▱▱▱▱▱▱▱▱▱▱▱▱\n'
                resposta += f'• BIN: <code>{bin_code}</code>\n'
                resposta += f'• BANDEIRA: <code>{brand}</code>\n'
                resposta += f'• TIPO: <code>{card_type}</code>\n'
                resposta += f'• NÍVEL: <code>{category}</code>\n'
                resposta += f'• BANCO: <code>{bank_name}</code>\n'
                resposta += f'• TEL BANCO: <code>{bank_phone}</code>\n'
                resposta += f'• URL: {bank_url}\n'
                resposta += f'• PAÍS: <code>{country_name}</code>\n'
                resposta += f'• ID: <code>{country_alpha3}</code>\n'
                resposta += f'• SIGLA: <code>{country_alpha2}</code>\n'
                resposta += f'▱▱▱▱▱▱▱▱▱▱▱▱▱\n'

                bot.reply_to(message, resposta, parse_mode='HTML')
            else:
                bot.reply_to(message, f'⚠️ {res.get("error", "Erro desconhecido")} ⚠️', parse_mode='HTML')
        except:
            bot.reply_to(message, '⚠️ DIGITE UMA BIN VÁLIDA! ⚠️', parse_mode='HTML')


def consultar_telefone1(message, args):
    chat_id = message.chat.id
    liberado_nome = PRIVADO + GRUPO + EXCEPT
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    if chat_id in liberado_nome:
        if len(args) < 2:
            bot.send_message(
                chat_id,
                "Uso incorreto do comando. Digite /telefone1 seguido pelo número de telefone desejado."
            )
            return

        telefs = args[1]

        # Verifique se o telefone fornecido possui apenas números
        if not telefs.isdigit():
            bot.send_message(
                chat_id,
                "Telefone inválido. Por favor, insira apenas números (sem espaços ou caracteres especiais)."
            )
            return

        # Verifique se o telefone fornecido tem 10 ou 11 dígitos
        if len(telefs) < 10 or len(telefs) > 11:
            bot.send_message(
                chat_id,
                "Telefone inválido. Por favor, insira um número de telefone com 10 ou 11 dígitos."
            )
            return

        try:
            start_time = time.time()  # Registrar o momento inicial

            response = requests.get(
                f'http://api2.minerdxc.tk:8080/api/telefone?numero={telefs}'
            )

            end_time = time.time()  # Registrar o momento após a chamada da API
            elapsed_time = end_time - start_time  # Calcular o tempo decorrido em segundos

            data = response.json()

            # Enviar a resposta da API para o bot, incluindo o tempo de resposta em segundos
            bot.send_message(
                chat_id,
                f"{data['message']}\nTempo de resposta da API: {elapsed_time:.2f} segundos"
            )
        except Exception as e:
            print("Erro ao consultar telefone:", str(e))
            bot.send_message(
                chat_id,
                "Ocorreu um erro ao consultar o telefone. Por favor, tente novamente mais tarde."
            )



def consultar_foto(message, args):
    chat_id = message.chat.id
    liberado_nome = PRIVADO + GRUPO + EXCEPT
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    if chat_id in liberado_nome:
        nomeCidadao = ' '.join(args[1:])  # O nome do cidadão a ser buscado

        try:
            response = requests.get(
                f'http://api2.minerdxc.tk:8080/api/foto?no_cidadao={nomeCidadao}'
            )
            data = response.json()

            if data.get('foto'):
                imageBase64 = data['foto']  # Foto em formato base64
                buffer = io.BytesIO(base64.b64decode(imageBase64))

                # Criar um objeto de imagem com o Pillow
                image = Image.open(buffer)

                # Salvar a imagem em um arquivo (opcional)
                image.save('foto_cidadao.jpg')

                # Enviar a foto como mensagem para o remetente
                bot.send_photo(chat_id, image, caption='Foto do cidadão')
            else:
                # Caso a API não retorne uma foto
                bot.reply_to(message, 'Foto não encontrada para esse cidadão.')
        except Exception as e:
            print('Erro ao buscar foto:', str(e))
            bot.reply_to(message, 'Ocorreu um erro ao buscar a foto.')



def consultar_nome(message, args):
    chat_id = message.chat.id
    liberado_nome = PRIVADO + GRUPO + EXCEPT
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    if chat_id in liberado_nome:
        # Verifique se foi fornecido um nome
        if len(args) < 2:
            bot.reply_to(message, "Por favor, insira um nome após o comando /nome.")
            return

        bot.reply_to(message, '<code>GERANDO O AQRUIVO...</code>', parse_mode='HTML')

        nome_comando = ' '.join(args[1:])

        try:
            startTime = time.perf_counter()  # Registrar o momento inicial

            url = f'http://api2.minerdxc.tk:8080/api/nomes?nome={nome_comando}'
            response = requests.get(url).json()

            endTime = time.perf_counter()  # Registrar o momento após a chamada da API
            elapsedTime = endTime - startTime  # Calcular o tempo decorrido em segundos

            data = response.get('message', '')  # Acesse a propriedade "message" da resposta

            # Use expressões regulares para extrair informações relevantes
            matches = re.findall(r'Nome: (.*?)\nCPF: (.*?)\nData de Nascimento: (.*?)\n', data)

            if matches:
                # Contar os nomes encontrados
                num_names_found = len(matches)

                # Formate os resultados com espaço entre os nomes
                formattedResult = '\n\n'.join([f"Nome: {match[0]}\nCPF: {match[1]}\nData de Nascimento: {match[2]}\n" for match in matches])

                # Nome do arquivo será o nome procurado
                file_name = f"{nome_comando}.txt"

                # Crie o conteúdo do arquivo de texto
                file_content = f"Nomes Encontrados: {num_names_found}\n\n{formattedResult}"

                # Salve o conteúdo no arquivo
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(file_content)

                # Envie o arquivo de texto
                with open(file_name, "rb") as file:
                    bot.send_document(chat_id, file)

                # Remova o arquivo temporário
                os.remove(file_name)

                # Envie a resposta formatada no Telegram
                bot.reply_to(message, f'<b>🔎 CONSULTA DE NOME 🔎</b>\n\nNomes Encontrados: {num_names_found}\nTempo de resposta da API: {elapsedTime:.2f} segundos', parse_mode='HTML')
            else:
                bot.reply_to(message, "Nenhum resultado encontrado para o nome fornecido.")
        except Exception as e:
            print(e)
            bot.reply_to(message, "Ocorreu um erro ao consultar o nome")


def consultar_cpffree(message, args):
    chat_id = message.chat.id
    liberado_nome = PRIVADO + GRUPO + EXCEPT
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    if chat_id in liberado_nome:
        nome5 = ' '.join(args[1:])


        if not nome5.isdigit() or len(nome5) != 11:
            bot.reply_to(message, "❌ CPF inválido. Por favor, insira um CPF válido com exatamente 11 dígitos numéricos, sem caracteres especiais ou espaços.")
            return



        try:
            response = requests.get(f'http://api2.minerdxc.tk:8080/api/cpf?cpf={nome5}')
            data = response.json()

            if data:
                formattedResult = 'Resultados da consulta CPF:\n'

                for entry in data:
                    formattedResult += '\n'  # Linha em branco entre cada entrada

                    # Use expressões regulares para extrair chaves e valores dentro das chaves {}
                    matches = re.findall(r'{(.*?)}', entry)

                    if matches:
                        for match in matches:
                            keyValuePairs = match.split(',')

                            # Formate cada par chave-valor
                            formattedPairs = []

                            for pair in keyValuePairs:
                                parts = pair.split(':', 1)
                                if len(parts) == 2:
                                    key, value = parts
                                    formattedKey = f'<b>{key.strip()}</b>'
                                    formattedPairs.append(f'{formattedKey}: {value.strip()}')

                            formattedResult += '\n\n'.join(formattedPairs)

                # Remova os espaços desnecessários entre as chaves e os valores
                formattedResult = formattedResult.replace('*:', '*')

                bot.reply_to(message, formattedResult, parse_mode='HTML')
            else:
                bot.reply_to(message, 'Nenhum resultado encontrado para o CPF fornecido.')
        except Exception as e:
            print('Erro ao consultar CPF:', str(e))
            bot.reply_to(message, 'Ocorreu um erro ao consultar o CPF.')



def consultar_cep(message, args):
    chat_id = message.chat.id
    bot.reply_to(message, '🔎 Aguarde estou buscando....🔎')
    if len(args) != 2:
        bot.reply_to(message, 'Insira o CEP após o comando!')
        return

    cep = args[1]

    try:
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        data = response.json()

        if 'erro' not in data:
            formatted_result = f'''
🔍 CONSULTA DE CEP 🔎
▱▱▱▱▱▱▱▱▱▱▱▱▱
• CEP: {data['cep']}
• UF: {data['uf']}
• CIDADE: {data['localidade']}
• BAIRRO: {data['bairro']}
• DDD: {data['ddd']}
▱▱▱▱▱▱▱▱▱▱▱▱▱
'''
            bot.reply_to(message, formatted_result)
        else:
            bot.reply_to(message, '⚠️ CEP NÃO ENCONTRADO ⚠️')
    except Exception as e:
        print('Erro ao consultar CEP:', str(e))
        bot.reply_to(message, 'Ocorreu um erro ao consultar o CEP.')



print('BOT ONLINE SKYNERD BUSCA @batmonn ✅!!!')

# Inicia a função enviar_mensagem_para_grupos em uma thread separada
#enviar_mensagem_thread = threading.Thread(target=enviar_mensagem_para_grupos)
#enviar_mensagem_thread.daemon = True
#enviar_mensagem_thread.start()

# Inicia o bot polling
bot.polling(none_stop=True)
