from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from typing import Union

from  models import Base


class Contato(Base):
    __tablename__ = 'contato'

    id = Column(Integer, primary_key=True)
    telefone = Column(String(15), unique=True)
    tipo = Column(String(10))
    data_insercao = Column(DateTime, default=datetime.now())

    # Definição do relacionamento entre o contato e um passageiro.
    # Aqui está sendo definido a coluna 'passageiro' que vai guardar
    # a referencia ao passageiro, a chave estrangeira que relaciona
    # um passageiro ao contato.
    passageiro = Column(Integer, ForeignKey("passageiro.pk_passageiro"), nullable=False)

    def __init__(self, telefone:str, tipo:str, data_insercao:Union[DateTime, None] = None):
        """
        Cria um Contato

        Arguments:
            telefone: o telefone do passageiro.
            tipo de contato: celular, fixo ou comercial.
            data_insercao: data de quando o contato foi feito ou inserido
                           à base
        """
        self.telefone = telefone
        self.tipo = tipo
        if data_insercao:
            self.data_insercao = data_insercao