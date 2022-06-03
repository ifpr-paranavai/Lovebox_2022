import sqlite3

dbconnect = sqlite3.connect('lovebox')
cursor = dbconnect.cursor()

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

def listar():
    return cursor.execute(
        'SELECT * FROM medicamentos INNER JOIN horarios WHERE medicamentos.id = horarios.id')

