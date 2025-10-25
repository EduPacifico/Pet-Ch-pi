from filaAgendamentos import filaAgendamentos
import json
import os

SCHEMA_MEDICOS = "./schema/baseDadosMedicos.json"
SCHEMA_AGENDAMENTOS = "./schema/baseDadosAgendamentos.json"

def notificarMedico():
    '''
    Remove o próximo agendamento da fila, valida com o JSON de médicos,
    simula a notificação e salva o agendamento no "banco de dados".
    '''
    
    if filaAgendamentos.empty():
        return {"status": 400, "mensagem": "Nenhum agendamento na fila."}

    agendamento = filaAgendamentos.get()
    
    try:
        id_medico_agendado = agendamento["id_medico"]
        horario_agendado = agendamento["data_hora"]
        pet_nome = agendamento["nome_pet"]
    except KeyError:
        filaAgendamentos.task_done()
        return {"status": 500, "mensagem": "Dados do agendamento incompletos!"}

    try:
        with open(SCHEMA_MEDICOS, "r", encoding='utf-8') as f:
            dadosMedicos = json.load(f)
    except FileNotFoundError:
        filaAgendamentos.task_done()
        return {"status": 500, "mensagem": f"Erro: {SCHEMA_MEDICOS} não encontrado."}

    medico_encontrado = None
    for medico in dadosMedicos.get('medicos', []):
        if medico["id"] == id_medico_agendado:
            medico_encontrado = medico
            break
            
    if not medico_encontrado:
        filaAgendamentos.task_done()
        return {"status": 404, "mensagem": f"Médico com ID {id_medico_agendado} não encontrado."}

    print(f"--- NOTIFICACAO ---")
    print(f"Para: {medico_encontrado['email_notificacao']}")
    print(f"Assunto: Novo Agendamento - {pet_nome} às {horario_agendado}")
    print(f"--- FIM NOTIFICACAO ---")

    try:
        try:
            with open(SCHEMA_AGENDAMENTOS, "r", encoding='utf-8') as f_agenda:
                dados_agenda = json.load(f_agenda)
                if 'agendamentos' not in dados_agenda:
                    dados_agenda['agendamentos'] = []
        except (FileNotFoundError, json.JSONDecodeError):
            dados_agenda = {"agendamentos": []}

        dados_agenda['agendamentos'].append(agendamento)
        
        with open(SCHEMA_AGENDAMENTOS, "w", encoding='utf-8') as f_agenda:
            json.dump(dados_agenda, f_agenda, indent=4)
            
    except Exception as e:
        filaAgendamentos.task_done()
        return {"status": 500, "mensagem": f"Erro ao salvar agendamento: {e}"}

    filaAgendamentos.task_done()
    return {"status": 200, 
            "mensagem": "Agendamento confirmado e médico notificado!"}