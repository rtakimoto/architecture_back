from pydantic import BaseModel
from typing import Optional, List
from models.passageiro import Passageiro

from schemas import ContatoSchema


class PassageiroSchema(BaseModel):
    """ Define como um novo passageiro a ser inserido deve ser representado
    """
    nome: str = "Joao da Silva"
    cpf: str = "433.345.437-26"
    flight: str = "TAM-1234"


class PassageiroUpdateSchema(BaseModel):
    """ Define como um passageiro a ser atualizado deve ser representado
    """
    id: int = 1
    nome: str = "Joao da Silva"
    cpf: str = "433.345.437-26"
    flight: str = "TAM-1234"

class PassageiroBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no nome do passageiro.
    """
    cpf: str = "433.345.437-26"


class ListagemPassageirosSchema(BaseModel):
    """ Define como uma listagem de passageiro será retornada.
    """
    passageiros:List[PassageiroUpdateSchema]


def apresenta_passageiros(passageiros: List[Passageiro]):
    """ Retorna uma representação do passageiro seguindo o schema definido em
        PassageiroSchema.
    """
    result = []
    for passageiro in passageiros:
        result.append({
            "id": passageiro.id,
            "nome": passageiro.nome,
            "cpf": passageiro.cpf,
            "flight": passageiro.flight,
        })

    return {"passageiros": result}


class PassageiroViewSchema(BaseModel):
    """ Define como um passageiro será retornado: passageiro + contatos.
    """
    id: int = 1
    nome: str = "Joao da Silva"
    cpf: str = "433.345.437-26"
    flight: str = "TAM-1234"
    total_contatos: int = 1
    contatos:List[ContatoSchema]


class PassageiroDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mesage: str
    nome: str



def apresenta_passageiro(passageiro: Passageiro):
    """ Retorna uma representação do passageiro seguindo o schema definido em
        PassageiroViewSchema.
    """
    contatos = []
    for contato in passageiro.contatos:
        contatos.append({
            "telefone": contato.telefone,
            "tipo": contato.tipo,
        })

    return {
        "id": passageiro.id,
        "nome": passageiro.nome,
        "cpf": passageiro.cpf,
        "flight": passageiro.flight,
        "total_contatos": len(passageiro.contatos),
        "contatos": contatos
    }
