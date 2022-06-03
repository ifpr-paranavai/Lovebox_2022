# Importando as bibliotecas
# import RPi.GPIO as GPIO
import time
import datetime
from db import crud

# import sqlite3
# import I2C_LCD_driver
'''
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


# Configurações iniciais do I2C, do buzzer e do LED de alarme
lcdi2c = I2C_LCD_driver.lcd()
buzzState = False
ledAlarmeState = False

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
'''
# Atualizando o horário da medicação (para testes)
crud.atualizarHorario('15:20', '15:16', 1)
crud.atualizarHorario('15:21', '15:30', 2)


# Atualizando o status de ingestão para 0 (para testes)
crud.atualizarStatusIngestao(0, 1)
crud.atualizarStatusIngestao(0, 2)



# Criando um loop infinito
while(True):
    # Selecionando os dados do banco de dados
    dadosBD = crud.listar()

    for dadoBD in dadosBD:
        horaAtual = datetime.datetime.now().strftime("%H:%M") # Armazena o horário atual em uma variável
            
        # Mudando os índices dos dados do banco para deixar o código mais intuitivo
        id = dadoBD[0]
        paciente = dadoBD[1]
        medicamento = dadoBD[2]
        dosagem = dadoBD[3]
        um = dadoBD[4]
        compartimento = dadoBD[5]
        statusTratamento = dadoBD[6]
        idHorario = dadoBD[7]
        id = dadoBD[8]
        horarioMedicacao = dadoBD[9]
        tempoLimite = dadoBD[10]
        statusIngestao = dadoBD[11]
        statusSincronizacao = dadoBD[12]

        print(paciente, horarioMedicacao, statusIngestao)


        # Se for o horário da medicação e ela não tiver sido ingerida
        if ((horaAtual == horarioMedicacao) and (statusIngestao == 0)):
            print('Disparar alarme')
            print(horarioMedicacao, paciente, medicamento, dosagem, um)

            # Exibe a mensagem no dispaly
            lcdi2c.lcd_clear()
            mensagemDisplay(horarioMedicacao, paciente, medicamento, dosagem, um)

            # Acende o LED do compartimento do medicamento
            GPIO.output(ledCompartimento[compartimento], True)            
            
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
                crud.atualizarStatusIngestao(1, idHorario) # Status de ingestão vai para 1
                semAlarme(compartimento) # O alarme para de tocar
                lcdi2c.lcd_display_string('Medicamento ingerido', 2, 0) # Exibe uma mensagem no display
            else:
                print('Não apertou o botao')
        
        
        # Se estiver no intervalo do tempo de ingestão e a medicação não tiver sido ingerida
        elif((horaAtual > horarioMedicacao) and (horaAtual < tempoLimite) and (statusIngestao == 0)):
            # Exibe a mensagem no dispaly
            lcdi2c.lcd_clear()
            mensagemDisplay(horaAtual, paciente, medicamento, dosagem, um)

            # Acende o LED do compartimento do medicamento
            GPIO.output(ledCompartimento[compartimento], True)

            # Acende o led alarme
            ledAlarmeState = True
            GPIO.output(ledAlarme, ledAlarmeState)

            time.sleep(5)
            
             # Se o botão for apertado
            if (GPIO.input(botao) == True):
                print('Apertou o botao no intervalo')
                crud.atualizarStatusIngestao(1, idHorario) # Status de ingestão vai para 1
                semAlarme(compartimento) # Some a mensagem do display e o o LED do compartimento apaga
                lcdi2c.lcd_display_string('Medicamento ingerido', 2, 0) # Exibe uma mensagem no display
            else:
                print('Não apertou o botao no intervalo')
        
        
        # Se for o horário limite para ingerir a medicação e ela não tiver sido ingerida
        elif ((horaAtual == tempoLimite) and (statusIngestao == 0)):
            print('Última chance de não atrasar')

            # Exibe a mensagem no dispaly
            lcdi2c.lcd_clear()
            mensagemDisplay(tempoLimite, paciente, medicamento, dosagem, um)

            # Acende o LED do compartimento do medicamento
            GPIO.output(ledCompartimento[compartimento], True)
            
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
                crud.atualizarStatusIngestao(1, idHorario) # Status de ingestão vai para 1
                semAlarme(compartimento)  # O alarme para de tocar
                lcdi2c.lcd_display_string('Medicamento ingerido', 2, 0) # Exibe uma mensagem no display
            else:
                print('Não apertou o botao')


        # Se a medicação não tiver sido ingerida dentro do tempo limite
        elif ((horaAtual > tempoLimite) and (statusIngestao == 0)):
            print('Não tocar - atrasou')

            # O alarme para de tocar
            semAlarme(compartimento)
            lcdi2c.lcd_clear()
            lcdi2c.lcd_display_string('Paciente ' + paciente + ' atrasou medicamento', 2, 0)
            time.sleep(5)


        else:
            lcdi2c.lcd_clear()
            lcdi2c.lcd_display_string('Lovebox', 2, 6)
            lcdi2c.lcd_display_string(horaAtual, 3, 7)
      
        # Se a medicação tiver sido ingerida dentro do tempo limite
        # if ((horaAtual > tempoLimite) and (statusIngestao == 1)):
        #     print('não tocar também - recarregando...')
        #     semAlarme(compartimento)  # O alarme para de tocar
        #     crud.atualizarStatusIngestao(0, idHorario) # Status de ingestão vai para 0
        
            
            
    time.sleep(10)        

