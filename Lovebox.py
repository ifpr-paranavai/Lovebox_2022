# Importando as bibliotecas
import RPi.GPIO as GPIO
import time
import datetime
import sqlite3
import I2C_LCD_driver

# Definindo como configurar a GPIO (físico)
GPIO.setmode(GPIO.BOARD)
# GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# Definindo os pinos dos componentes
ledAlarme = int(40)
# ledAlarme = 13
ledCompartimento = [int(38), int(36)]
# ledCompartimento = [12, 5]
buzzer = int(32)
# buzzer = 23
botao = int(26)
# botao = 26


# Definindo os pinos dos LED's e do buzzer como saídas
GPIO.setup(ledAlarme, GPIO.OUT)
for compartimento in range(0,2):
    GPIO.setup(ledCompartimento[compartimento], GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)


# Definindo o pino do botão como entrada
GPIO.setup(botao, GPIO.IN)


# Configurações iniciais do bando de dados, do I2C, do buzzer e do LED de alarme
dbconnect = sqlite3.connect('lovebox')
cursor = dbconnect.cursor()
lcdi2c = I2C_LCD_driver.lcd()
buzzState = False
ledAlarmeState = False


def atualizarHorario(horaAlarme, tempoLimite, idHorario):
    cursor.execute('''
        UPDATE horarios
        SET horarioMedicacao = ?
        , tempoLimite = ?
        WHERE idHorario = ?;
    ''', (horaAlarme, tempoLimite, idHorario,))
    dbconnect.commit()

def atualizarStatusIngestao(statusIngestao, idHorario):
    cursor.execute('''
        UPDATE horarios
        SET statusIngestao = ?
        WHERE idHorario = ?;
    ''', (statusIngestao, idHorario,))
    dbconnect.commit()


def mensagemDisplay(horario, paciente, medicamento, dosagem, unidadeMedida):
    hora = str('Horario: ' + horario)
    pac = str('Paciente: ' + paciente)
    medicacao = str('Medic.: ' + medicamento)
    dose = str('Dosagem: ' + str(dosagem) + unidadeMedida)

    lcdi2c.lcd_display_string(hora, 1, 0)
    lcdi2c.lcd_display_string(pac, 2, 0)
    lcdi2c.lcd_display_string(medicacao, 3, 0)
    lcdi2c.lcd_display_string(dose, 4, 0)

def semAlarme(compartimento):
    lcdi2c.lcd_clear()
    GPIO.output(ledCompartimento[compartimento], False)
    ledAlarmeState = False
    GPIO.output(ledAlarme, ledAlarmeState)

# Atualizando o horário da medicação (para testes)
atualizarHorario('15:14', '15:16', 1)
atualizarHorario('15:14', '15:30', 2)


# Atualizando o status de ingestão para 0 (para testes)
atualizarStatusIngestao(0, 1)
atualizarStatusIngestao(0, 2)


# Criando um loop infinito
while(True):
    # Selecionando os dados do banco de dados
    dadosBD = cursor.execute('SELECT * FROM medicamentos INNER JOIN horarios WHERE medicamentos.id = horarios.id')
	

    for dadoBD in dadosBD:
        horaAtual = datetime.datetime.now().strftime("%H:%M") # Armazena o horário atual em uma variável
        
        
        # Mudando os índices dos dados do banco para deixar o código mais intuitivo
        dados = dict()
        dados['id'] = dadoBD[0]
        dados['paciente'] = dadoBD[1]
        dados['medicamento'] = dadoBD[2]
        dados['dosagem'] = dadoBD[3]
        dados['um'] = dadoBD[4]
        dados['compartimento'] = dadoBD[5]
        dados['statusTratamento'] = dadoBD[6]
        dados['idHorario'] = dadoBD[7]
        dados['id'] = dadoBD[8]
        dados['horarioMedicacao'] = dadoBD[9]
        dados['tempoLimite'] = dadoBD[10]
        dados['statusIngestao'] = dadoBD[11]
        dados['statusSincronizacao'] = dadoBD[12]


        # Se for o horário da medicação e ela não tiver sido ingerida
        if ((horaAtual == dados['horarioMedicacao']) and (dados['statusIngestao'] == 0)):
            print('Disparar alarme')
            print(dados['horarioMedicacao'], dados['paciente'], dados['medicamento'], dados['dosagem'], dados['um'])

            # Exibe a mensagem no dispaly
            lcdi2c.lcd_clear()
            mensagemDisplay(dados['horarioMedicacao'], dados['paciente'], dados['medicamento'], dados['dosagem'], dados['um'])

            # Acende o LED do compartimento do medicamento
            GPIO.output(ledCompartimento[(dados['compartimento'])], True)            
            
            # Toca o alarme
            ledAlarmeState = False
            for cont in range(0, 6):
                buzzState = not buzzState
                GPIO.output(buzzer, buzzState)

                ledAlarmeState = not ledAlarmeState
                GPIO.output(ledAlarme, ledAlarmeState)
                time.sleep(1)

            time.sleep(5)

            # Se o botão for apertado
            if (GPIO.input(botao) == True):
                print('Apertou o botao')
                atualizarStatusIngestao(1, dados['idHorario']) # Status de ingestão vai para 1
                semAlarme(dados['compartimento']) # O alarme para de tocar
                lcdi2c.lcd_display_string('Medicamento ingerido', 2, 0) # Exibe uma mensagem no display
            else:
                print('Não apertou o botao')
        
        
        # Se estiver no intervalo do tempo de ingestão e a medicação não tiver sido ingerida
        elif((horaAtual > dados['horarioMedicacao']) and (horaAtual < dados['tempoLimite']) and (dados['statusIngestao'] == 0)):
            # Exibe a mensagem no dispaly
            lcdi2c.lcd_clear()
            mensagemDisplay(horaAtual, dados['paciente'], dados['medicamento'], dados['dosagem'], dados['um'])

            # Acende o LED do compartimento do medicamento
            GPIO.output(ledCompartimento[(dados['compartimento'])], True)

            # Acende o led alarme
            ledAlarmeState = True
            GPIO.output(ledAlarme, ledAlarmeState)

            time.sleep(5)
            
             # Se o botão for apertado
            if (GPIO.input(botao) == True):
                print('Apertou o botao no intervalo')
                atualizarStatusIngestao(1, dados['idHorario']) # Status de ingestão vai para 1
                semAlarme(dados['compartimento']) # Some a mensagem do display e o o LED do compartimento apaga
                lcdi2c.lcd_display_string('Medicamento ingerido', 2, 0) # Exibe uma mensagem no display
            else:
                print('Não apertou o botao no intervalo')
        
        
        # Se for o horário limite para ingerir a medicação e ela não tiver sido ingerida
        elif ((horaAtual == dados['tempoLimite']) and (dados['statusIngestao'] == 0)):
            print('Última chance de não atrasar')

            # Exibe a mensagem no dispaly
            lcdi2c.lcd_clear()
            mensagemDisplay(dados['tempoLimite'], dados['paciente'], dados['medicamento'], dados['dosagem'], dados['um'])

            # Acende o LED do compartimento do medicamento
            GPIO.output(ledCompartimento[(dados['compartimento'])], True)
            
            # Toca o alarme
            ledAlarmeState = False
            for cont in range(0, 6):
                buzzState = not buzzState
                GPIO.output(buzzer, buzzState)

                ledAlarmeState = not ledAlarmeState
                GPIO.output(ledAlarme, ledAlarmeState)
                time.sleep(1)

            time.sleep(5)

            # Se o botão for pressionado
            if (GPIO.input(botao) == True):
                print('Apertou o botao')
                atualizarStatusIngestao(1, dados['idHorario']) # Status de ingestão vai para 1
                semAlarme(dados['compartimento'])  # O alarme para de tocar
                lcdi2c.lcd_display_string('Medicamento ingerido', 2, 0) # Exibe uma mensagem no display
            else:
                print('Não apertou o botao')


        # Se a medicação não tiver sido ingerida dentro do tempo limite
        elif ((horaAtual > dados['tempoLimite']) and (dados['statusIngestao'] == 0)):
            print('Não tocar - atrasou')

            # O alarme para de tocar
            semAlarme(dados['compartimento'])
            lcdi2c.lcd_clear()
            lcdi2c.lcd_display_string('Paciente ' + dados['paciente'] + ' atrasou medicamento', 2, 0)
            time.sleep(5)


        else:
            lcdi2c.lcd_clear()
            lcdi2c.lcd_display_string('Lovebox', 2, 6)
            lcdi2c.lcd_display_string(horaAtual, 3, 7)
      
        # Se a medicação tiver sido ingerida dentro do tempo limite
        if ((horaAtual > dados['tempoLimite']) and (dados['statusIngestao'] == 1)):
            print('não tocar também - recarregando...')
            semAlarme(dados['compartimento'])  # O alarme para de tocar
            atualizarStatusIngestao(0, dados['idHorario']) # Status de ingestão vai para 0
        
            
            
    time.sleep(10)        

