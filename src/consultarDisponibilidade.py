import json
from datetime import datetime, time, timedelta

SCHEMA_MEDICOS = "./schema/baseDadosMedicos.json"
SCHEMA_AGENDAMENTOS = "./schema/baseDadosAgendamentos.json"

def consultarDisponibilidade(especialidade_desejada, data_desejada_str):
    '''
    Verifica a disponibilidade de médicos por especialidade em uma data.
    Retorna o primeiro horário livre (slot de 1h) encontrado.
    '''
    
    try:
        with open(SCHEMA_MEDICOS, "r", encoding='utf-8') as f:
            dadosMedicos = json.load(f)
        with open(SCHEMA_AGENDAMENTOS, "r", encoding='utf-8') as f:
            dadosAgendamentos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"status": 500, "mensagem": "Erro ao ler arquivos de schema."}

    medicos_da_especialidade = [
        m for m in dadosMedicos.get('medicos', []) 
        if m['especialidade'].lower() == especialidade_desejada.lower()
    ]
    
    if not medicos_da_especialidade:
        return {"status": 404, "mensagem": "Nenhum médico encontrado para esta especialidade."}

    try:
        data_obj = datetime.strptime(data_desejada_str, "%Y-%m-%d").date()
    except ValueError:
        return {"status": 400, "mensagem": "Formato de data inválido. Use YYYY-MM-DD."}

    agendamentos_marcados = set()
    for ag in dadosAgendamentos.get('agendamentos', []):
        agendamentos_marcados.add( (ag['id_medico'], ag['data_hora']) )

    for medico in medicos_da_especialidade:
        try:
            inicio_str, fim_str = medico['horario_trabalho'].split('-')
            hora_inicio = datetime.strptime(inicio_str, "%H:%M").hour
            hora_fim = datetime.strptime(fim_str, "%H:%M").hour
            
            hora_atual = hora_inicio
            while hora_atual < hora_fim:
                slot_datetime = datetime.combine(data_obj, time(hour=hora_atual))
                slot_iso = slot_datetime.isoformat()
                
                if (medico['id'], slot_iso) not in agendamentos_marcados:
                    return {
                        "status": 200,
                        "mensagem": "Horário disponível encontrado.",
                        "medico": medico['nome'],
                        "especialidade": medico['especialidade'],
                        "horario_disponivel": slot_iso
                    }
                
                hora_atual += 1

        except Exception as e:
            print(f"(Erro) Ao processar horário do Dr. {medico['nome']}: {e}")
            continue
            
    return {
        "status": 404,
        "mensagem": "Nenhum horário disponível para esta especialidade na data selecionada."
    }

if __name__ == "__main__":
    print("\n--- Testando EXTRA: Consulta de Disponibilidade ---")
    
    print("\nBuscando 'Clínico Geral' em 2025-11-20...")
    dispo_cg = consultarDisponibilidade("Clínico Geral", "2025-11-20")
    print(f"Resultado: {dispo_cg}")
    
    print("\nBuscando 'Cardiologia' em 2025-11-20...")
    dispo_cardio = consultarDisponibilidade("Cardiologia", "2025-11-20")
    print(f"Resultado: {dispo_cardio}")

    print("\nBuscando 'Inexistente' em 2025-11-20...")
    dispo_err = consultarDisponibilidade("Inexistente", "2025-11-20")
    print(f"Resultado: {dispo_err}")