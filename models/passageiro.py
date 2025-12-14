from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from  models import Base, Contato


class Passageiro(Base):
    __tablename__ = 'passageiro'

    id = Column("pk_passageiro", Integer, primary_key=True)
    nome = Column(String(140))
    cpf = Column(String(14), unique=True)
    flight = Column(String(8))
    data_insercao = Column(DateTime, default=datetime.now())

    # Definição do relacionamento entre o passageiro e o contato.
    # Essa relação é implicita, não está salva na tabela 'passageiro',
    # mas aqui estou deixando para SQLAlchemy a responsabilidade
    # de reconstruir esse relacionamento.
    contatos = relationship("Contato")

    def __init__(self, nome:str, cpf:str, flight:str,
                 data_insercao:Union[DateTime, None] = None):
        """
        Cria um Passageiro

        Arguments:
            nome: nome do passageiro.
            cpf: CPF do passageiro
            peso: peso do passageiro
            data_insercao: data de quando o passageiro foi inserido à base
        """
        self.nome = nome
        self.cpf = cpf
        self.flight = flight

        # se não for informada, será o data exata da inserção no banco
        if data_insercao:
            self.data_insercao = data_insercao

    def adiciona_contato(self, contato:Contato):
        """ Adiciona um novo Contato do Passageiro
        """
        self.contatos.append(contato)

