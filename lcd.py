import I2C_LCD_driver

lcdi2c = I2C_LCD_driver.lcd()

def mensagemDisplay(horario, paciente, medicamento, dosagem, unidadeMedida):
    hora = str('Horario: ' + horario)
    pac = str('Paciente: ' + paciente)
    medicacao = str('Medic.: ' + medicamento)
    dose = str('Dosagem: ' + str(dosagem) + unidadeMedida)

    exibirMensagem(hora, 1, 0)
    exibirMensagem(pac, 2, 0)
    exibirMensagem(medicacao, 3, 0)
    exibirMensagem(dose, 4, 0)

def limparDisplay():
    lcdi2c.lcd_clear()

def exibirMensagem(mensagem, linha, coluna):
    lcdi2c.lcd_display_string(mensagem, linha, coluna)
