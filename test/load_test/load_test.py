from locust import HttpUser, between, task


class LoadTest(HttpUser):
    """
    Configurando um teste de carga com o Locust
    """
    wait_time = between(1, 3)

    @task
    def add_passageiro(self):
        """ Fazendo a inserção de passageiros.
        """

        # criando o passageiro
        passageiro = {
            'birthdate': '1974-10-05T00:00:00',
            'cpf': '27036343826',
            'flight': 'TAM-1234',
            'nome': 'Joao da Silva'
        }

        # configurando a requisição
        headers = {'Content-Type': 'multipart/form-data'}
        response = self.client.post('passageiro', data=passageiro, headers=headers)

        # verificando a resposta
        data_response = response.json()
        if response.status_code == 200:
            print("Passageiro %s salvo na base" % passageiro["nome"])
        elif response.status_code == 409:
            print(data_response["message"] + passageiro["nome"])
        else:
            print('Falha na rota de adição de um passageiro')

    @task
    def listagem(self):
        """ Fazendo uma listagem dos passageiros salvos.
        """
        # configurando a requisição
        response = self.client.get('passageiros')
    
        # verificando a resposta
        data = response.json()
        if response.status_code == 200:
            print('Total de passageiros salvos: %d' % len(data["passageiros"]))
        else:
            print('Falha na rota /passageiros')

    @task
    def get_passageiro(self):
        """ Fazendo uma busca pelo passageiro de id 27036343826.
        """
        # configurando a requisição
        response = self.client.get('passageiro?cpf=27036343826')
    
        # verificando a resposta
        data = response.json()
        if response.status_code == 200:
            print('Passageiro retornado: %s' % data["nome"])
        else:
            print('Falha na rota /passageiro?cpf=27036343826')

    @task
    def situacao_cpf_valido(self):
        """ Fazendo a checagem da situacao de cpf 27036343826 e data de nascimento 1974-05-19.
        """
        # configurando a requisição
        response = self.client.get('external-data?cpf=27036343826&birthdate=1974-05-19')
    
        # verificando a resposta
        data = response.json()
        if response.status_code == 200:
            print('CPF retornado: %s' % data["situacao"])
        else:
            print('Falha na rota /external-data')
