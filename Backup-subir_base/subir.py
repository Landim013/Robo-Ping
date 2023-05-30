import pandas as pd
import mysql.connector
from mysql.connector import Error

con = mysql.connector.connect(host='127.0.0.1', database='clientes2', 
                              user='root', password='')

try:
    if con.is_connected():
        db_info = con.get_server_info()
        print('Conectado ao servidor MySQL versão ', db_info)
        cursor = con.cursor()
        cursor.execute("select database();")
        linha = cursor.fetchone()
        print("Conectado ao banco de dados ", linha)

        arquivo = pd.read_excel('Radios B2B instalados.xlsx')

        quant = arquivo['ID'].count()

        for i in range(0, quant):
            id_vantive = str(arquivo['ID'][i]).strip()
            id_vantive = id_vantive.replace('.0', '')
            cliente = str(arquivo['CLIENTE'][i]).replace("'", " ")
            ip = str(arquivo['IP SWT'][i])


            sla = str(arquivo['SLA'][i])
            sla = sla.replace('%', '')
            #print(sla)
            if(sla == '99.3'):
                sla = '99,30'
            elif(sla == '99.7'):
                sla = '99,70'
            elif(sla == '99.5'):
                sla = '99,50'
            elif(sla == '99.99'):
                sla = '99,99'
            elif(sla == '99,3'):
                sla = '99,30'
            else:
                sla = 'S/SLA'

            #print(f"{i} - SLA: {sla} - IP: {ip}")
           
            inserir = """INSERT INTO pings (id_vantive, cliente, ip, situacao, tipo_cliente,
             sla, vezes_off)
             VALUES('{}', '{}', '{}', {}, 'RADIO', '{}', 0);""".format(id_vantive, cliente, ip, True, sla)
            
            print(inserir)
            cursor.execute(inserir)
            con.commit()
        
    cursor.close()

except Error as e:
    print(e)

finally:   
    if con.is_connected():
        cursor.close()
        con.close()
        print("Conexão ao MySQL foi encerrada.")
       