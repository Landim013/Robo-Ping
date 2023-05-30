import mysql.connector
from mysql.connector import Error
from subprocess import Popen, PIPE
import subprocess
from datetime import datetime, time
import time
import requests

from constantes import HOST_INACESSIVEL, PING, SLEEP, VEZES

def send_message(token, chat_id, message):
    try:
        data = {"chat_id": chat_id, "text": message}
        url = "https://api.telegram.org/bot{}/sendMessage".format(token)
        requests.post(url, data)
    except Exception as e:
        print('Erro no sendMessage: ', e)

con = mysql.connector.connect(host='127.0.0.1', database='clientes2', 
                              user='root', password='')

try:
    if con.is_connected():
        while(True):
            db_info = con.get_server_info()
            print('Conectado ao servidor MySQL versão ', db_info)
            cursor = con.cursor()
            cursor.execute("select database();")
            linha = cursor.fetchone()
            print("Conectado ao banco de dados ", linha)

            query = """SELECT id_programa, ip, vezes_off, id_vantive, cliente, sla, ponta, id_associado 
                            FROM pings WHERE tipo_cliente = 'ALTO TIETE';"""
            cursor.execute(query)

            linhas = cursor.fetchall()
            ativos = 0
            inativos = 0
            for linha in linhas :
                id_prog = linha[0]
                ip = linha[1]
                vezes = int(linha[2]) 
                id_vantive = linha[3]
                cliente = linha[4]
                sla = linha[5]
                ponta = linha[6]
                id_associado = linha[7]
                resposta = subprocess.run('ping {} -n {}'.format(ip, PING), stdout=PIPE)
                rede_destino = str(resposta)
                if(resposta.returncode == 0 and HOST_INACESSIVEL not in rede_destino):
                    ativos += 1
                    update = "UPDATE pings SET situacao = true WHERE id_programa = {}".format(id_prog)
                    update_vezes = "UPDATE pings SET vezes_off = 0 WHERE id_programa = {}".format(id_prog)
                    cursor.execute(update_vezes)

                else:
                    vezes += 1
                    inativos += 1
                    if(vezes == VEZES):
                        
                        token = '5314422542:AAGbXECqxtq3CCLIVErgK46G2X6X1tEbdlk'
                        chat_id = '-844737653'

                        msg = """MONITORAMENTO\n**CLIENTE FORA**
                        \n\nTipo de cliente: ALTO TIETÊ\nSLA: {}\nCliente: {}\nId Vantive: {}\nIP: {}""".format(sla, cliente, id_vantive, ip)
                        
                        if(id_associado != ""):
                            busca_id_associado = """SELECT cliente, ponta, situacao, ip, id_vantive, tipo_cliente FROM pings 
                            WHERE id_vantive = '{}' 
                            AND tipo_cliente = 'ALTO TIETE';""".format(id_associado)

                            cursor.execute(busca_id_associado)
                            linhas_id_associado = cursor.fetchall()
                            for li in linhas_id_associado:
                                a_cliente = li[0]
                                a_ponta = li[1]
                                a_situacao = li[2]
                                a_ip = li[3]
                                a_id_vantive = li[4]
                                a_tipo_cliente = li[5]
                                divisoria = 50 * "-"
                                if(a_situacao == 1): 
                                    a_situacao = "OK" 
                                else: 
                                    a_situacao = "FORA"
                                msg_complemento = """\n{}\nSTATUS LINK BACKUP\nLink Backup\n\nID Vantive: {}\nCliente: {}\nTipo Cliente: {}\nPonta: {}\nSituação: {}\nIP: {}""".format(
                                    divisoria, a_id_vantive, a_cliente, a_tipo_cliente, a_ponta, a_situacao, a_ip)

                                msg = msg + msg_complemento

                        send_message(token, chat_id, msg)

                    update = "UPDATE pings SET situacao = false WHERE id_programa = {}".format(id_prog)
                    update_vezes = "UPDATE pings SET vezes_off = {} WHERE id_programa = {}".format(vezes, id_prog)
                    cursor.execute(update_vezes)

                cursor.execute(update)
                con.commit()
                print("ID: {} --- IP: {}".format(id_prog, ip))
                print("Tipo de cliente: ALTO TIETE")
            
            horario = datetime.today().strftime('%d/%m %H:%M')
            inserir_hora = "INSERT INTO horarios (ultimo_ping, tipo_cliente) values('{}', 'ALTO TIETE')".format(horario)    
            cursor.execute(inserir_hora)
            con.commit()
            print("Ativos: {} \nInativos: {}".format(ativos, inativos))
            print('Fimmmmmmmmmmmmmmmmmmmm')
            time.sleep(SLEEP)

            cursor.close()
            

except Error as e:
    print(e)

finally:   
    if con.is_connected():
        cursor.close()
        con.close()
        print("Conexão ao MySQL foi encerrada.")