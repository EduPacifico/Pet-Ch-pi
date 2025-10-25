from filaAgendamentos import filaAgendamentos
 
def submeterAgendamento(agendamento):
    '''
    Adiciona um novo agendamento à fila de processamento.
    
    Exemplo de 'agendamento' (dict):
    {"id_medico": 1, 
     "id_usuario": 100, 
     "nome_pet": "Bolinha",
     "data_hora": "2025-11-21T11:00:00"
    }
    '''
    try:
        filaAgendamentos.put(agendamento)
        print(f"(Sistema) Agendamento para {agendamento['nome_pet']} submetido à fila.")
        return True
    except Exception as e:
        print(f"(Sistema) Erro ao submeter agendamento: {e}")
        return False