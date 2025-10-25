
import unittest
import json
from unittest.mock import patch, mock_open


import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from consultarDisponibilidade import consultarDisponibilidade


MOCK_MEDICOS = {
    "medicos": [
        {
            "id": 1, "nome": "Dr. Marlon (Madrugador)", "especialidade": "Clínico Geral",
            "email_notificacao": "marlon.ferrari@petchopi.com", "horario_trabalho": "08:00-12:00"
        },
        {
            "id": 2, "nome": "Dra. Ana (Normal)", "especialidade": "Clínico Geral",
            "email_notificacao": "ana.silva@petchopi.com", "horario_trabalho": "09:00-17:00"
        },
        {
            "id": 3, "nome": "Dr. Vet (Cardio)", "especialidade": "Cardiologia",
            "email_notificacao": "joao.vet@petchopi.com", "horario_trabalho": "10:00-14:00"
        }
    ]
}

MOCK_AGENDAMENTOS_VAZIO = {"agendamentos": []}

MOCK_AGENDAMENTOS_CASO_2 = {
    "agendamentos": [
        
        {"id_medico": 1, "id_usuario": 100, "nome_pet": "Rex", "data_hora": "2025-10-25T08:00:00"},
       
    ]
}

MOCK_AGENDAMENTOS_CASO_3 = {
    "agendamentos": [
       
        {"id_medico": 1, "id_usuario": 100, "nome_pet": "Rex", "data_hora": "2025-10-25T08:00:00"},
       
        {"id_medico": 2, "id_usuario": 101, "nome_pet": "Mimi", "data_hora": "2025-10-25T09:00:00"},
       
        {"id_medico": 2, "id_usuario": 102, "nome_pet": "Fido", "data_hora": "2025-10-26T09:00:00"},
    ]
}

MOCK_AGENDAMENTOS_CASO_4_LOTADO = {
    "agendamentos": [
       
        {"id_medico": 3, "id_usuario": 100, "nome_pet": "A", "data_hora": "2025-10-25T10:00:00"},
        {"id_medico": 3, "id_usuario": 101, "nome_pet": "B", "data_hora": "2025-10-25T11:00:00"},
        {"id_medico": 3, "id_usuario": 102, "nome_pet": "C", "data_hora": "2025-10-25T12:00:00"},
        {"id_medico": 3, "id_usuario": 103, "nome_pet": "D", "data_hora": "2025-10-25T13:00:00"},
    ]
}



class TestDisponibilidade(unittest.TestCase):

    def mock_json_open(self, mock_medicos_data, mock_agendamentos_data):
        """
        Helper para mocar as duas chamadas 'open'.
        Ele intercepta 'open(nome_arquivo)' e retorna o JSON falso 
        correspondente.
        """
        
        mock_medicos_str = json.dumps(mock_medicos_data)
        mock_agendamentos_str = json.dumps(mock_agendamentos_data)

    
        mock_files = {
            './schema/baseDadosMedicos.json': mock_open(read_data=mock_medicos_str),
            './schema/baseDadosAgendamentos.json': mock_open(read_data=mock_agendamentos_str)
        }

        def mock_open_side_effect(filename, *args, **kwargs):
            if filename in mock_files:
                return mock_files[filename].return_value
      
            raise FileNotFoundError(f"Mocked 'open' não encontrou: {filename}")
            
        return mock_open_side_effect

    def test_cenario_1_clinico_geral_agenda_vazia(self):
        """
        Cenário: 'Clínico Geral'. 
        Dr. Marlon (inicia 08:00) e Dra. Ana (inicia 09:00) estão livres.
        Deve retornar o mais cedo: Dr. Marlon @ 08:00.
        """
        mock_open_func = self.mock_json_open(MOCK_MEDICOS, MOCK_AGENDAMENTOS_VAZIO)
        
        with patch('builtins.open', mock_open_func):
            resultado = consultarDisponibilidade("Clínico Geral", "2025-10-25")
        
        self.assertEqual(resultado["status"], 200)
        self.assertEqual(resultado["horario_disponivel"], "2025-10-25T08:00:00")
        self.assertEqual(resultado["medico"], "Dr. Marlon (Madrugador)")

    def test_cenario_2_clinico_geral_primeiro_horario_ocupado(self):
        """
        Cenário: 'Clínico Geral'.
        Dr. Marlon (08:00) está OCUPADO.
        Dra. Ana (09:00) está LIVRE.
        O próximo horário mais cedo é 09:00.
        No desempate das 09:00, "Dr. Marlon" vem ANTES de "Dra. Ana".
        Deve retornar Dr. Marlon @ 09:00.
        """
        mock_open_func = self.mock_json_open(MOCK_MEDICOS, MOCK_AGENDAMENTOS_CASO_2)
        
        with patch('builtins.open', mock_open_func):
            resultado = consultarDisponibilidade("Clínico Geral", "2025-10-25")
            
        self.assertEqual(resultado["status"], 200)
        self.assertEqual(resultado["horario_disponivel"], "2025-10-25T09:00:00")
        
     
        self.assertEqual(resultado["medico"], "Dr. Marlon (Madrugador)")

    def test_cenario_3_clinico_geral_ambos_ocupados_no_inicio(self):
        """
        Cenário: 'Clínico Geral'.
        Dr. Marlon (08:00) está OCUPADO.
        Dra. Ana (09:00) está OCUPADA.
        O próximo horário livre mais cedo é do Dr. Marlon às 09:00.
        (A Dra. Ana só estará livre às 10:00).
        Deve retornar Dr. Marlon @ 09:00.
        """
        mock_open_func = self.mock_json_open(MOCK_MEDICOS, MOCK_AGENDAMENTOS_CASO_3)
        
        with patch('builtins.open', mock_open_func):
            resultado = consultarDisponibilidade("Clínico Geral", "2025-10-25")
            
        self.assertEqual(resultado["status"], 200)
        self.assertEqual(resultado["horario_disponivel"], "2025-10-25T09:00:00")
        self.assertEqual(resultado["medico"], "Dr. Marlon (Madrugador)")
        
    def test_cenario_4_especialidade_lotada(self):
        """
        Cenário: 'Cardiologia'.
        Dr. Vet (10:00-14:00) está com TODOS os horários ocupados.
        Deve retornar 404 "Nenhum horário disponível".
        """
        mock_open_func = self.mock_json_open(MOCK_MEDICOS, MOCK_AGENDAMENTOS_CASO_4_LOTADO)
        
        with patch('builtins.open', mock_open_func):
            resultado = consultarDisponibilidade("Cardiologia", "2025-10-25")
            
        self.assertEqual(resultado["status"], 404)
        self.assertIn("Nenhum horário disponível", resultado["mensagem"])

    def test_cenario_5_especialidade_inexistente(self):
        """
        Cenário: 'Dermatologia' (não existe no mock).
        Deve retornar 404 "Nenhum médico encontrado".
        """
        mock_open_func = self.mock_json_open(MOCK_MEDICOS, MOCK_AGENDAMENTOS_VAZIO)
        
        with patch('builtins.open', mock_open_func):
            resultado = consultarDisponibilidade("Dermatologia", "2025-10-25")
            
        self.assertEqual(resultado["status"], 404)
        self.assertIn("Nenhum médico encontrado", resultado["mensagem"])

    def test_cenario_6_data_formato_invalido(self):
        """
        Cenário: Data em formato "DD/MM/YYYY".
        Deve retornar 400 "Formato de data inválido".
        """
      
        resultado = consultarDisponibilidade("Clínico Geral", "25/10/2025")
        
        self.assertEqual(resultado["status"], 400)
        self.assertIn("Formato de data inválido", resultado["mensagem"])
        
    def test_cenario_7_json_nao_encontrado(self):
        """
        Cenário: Arquivos JSON não são encontrados.
        Deve retornar 500 "Erro ao ler arquivos de schema".
        """
   
        mock_open_with_error = mock_open()
        mock_open_with_error.side_effect = FileNotFoundError
        
        with patch('builtins.open', mock_open_with_error):
            resultado = consultarDisponibilidade("Clínico Geral", "2025-10-25")
            
        self.assertEqual(resultado["status"], 500)
        self.assertIn("Erro ao ler arquivos de schema", resultado["mensagem"])

if __name__ == '__main__':
    print("======================================================")
    print("Executando testes elaborados para 'consultarDisponibilidade'")
    print("======================================================")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)