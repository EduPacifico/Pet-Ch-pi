import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from filaAgendamentos import filaAgendamentos
from submeterAgendamento import submeterAgendamento
from notificarMedico import notificarMedico
import json
import time

def setup_test_environment():
    """ Limpa a fila antes de cada teste """
    while not filaAgendamentos.empty():
        try:
            filaAgendamentos.get(block=False)
        except Exception:
            pass
        filaAgendamentos.task_done()
    print("\n--- Setup Teste: Fila limpa ---")

def test_notificarMedico_success():
    """ Teste de ponta a ponta (Submissão -> Fila -> Notificação) """
    setup_test_environment()
    
    payload = {
        "id_medico": 1, 
        "id_usuario": 102, 
        "nome_pet": "Fofinho (Teste Sucesso)",
        "data_hora": "2025-11-21T15:00:00"
    }
    
    print(f"Submetendo agendamento: {payload['nome_pet']}")
    submeterAgendamento(payload)
    
    print("Processando fila (notificarMedico)...")
    resultado = notificarMedico()
    
    print(f"Resultado: {resultado}")
    assert resultado["status"] == 200
    assert "notificado" in resultado["mensagem"]

def test_notificarMedico_fail_campos_incompletos():
    """ Teste de falha: Payload sem campos obrigatórios """
    setup_test_environment()
    
    payload = {
        "id_medico": 1, 
        "nome_pet": "Sem Data (Teste Falha)"
    }
    
    print(f"Submetendo agendamento: {payload['nome_pet']}")
    submeterAgendamento(payload)
    
    print("Processando fila (notificarMedico)...")
    resultado = notificarMedico()
    
    print(f"Resultado: {resultado}")
    assert resultado["status"] == 500
    assert "incompletos" in resultado["mensagem"]

def test_notificarMedico_fail_medico_nao_encontrado():
    """ Teste de falha: ID do médico não existe no JSON """
    setup_test_environment()
    
    payload = {
        "id_medico": 999,
        "id_usuario": 103, 
        "nome_pet": "Fantasma (Teste Falha)",
        "data_hora": "2025-11-21T16:00:00"
    }
    
    print(f"Submetendo agendamento: {payload['nome_pet']}")
    submeterAgendamento(payload)
    
    print("Processando fila (notificarMedico)...")
    resultado = notificarMedico()
    
    print(f"Resultado: {resultado}")
    assert resultado["status"] == 404
    assert "não encontrado" in resultado["mensagem"]

# --- Execução dos Testes ---
if __name__ == "__main__":
    print("=================================")
    print("  Executando Testes - Pet Chópi  ")
    print("=================================")
    
    test_notificarMedico_success()
    
    time.sleep(1) # Pequena pausa para legibilidade
    test_notificarMedico_fail_campos_incompletos()
    
    time.sleep(1) # Pequena pausa para legibilidade
    test_notificarMedico_fail_medico_nao_encontrado()
    
    print("\n=================================")
    print("         Testes Concluídos         ")
    print("=================================")