from pydantic import BaseModel


class ContatoSchema(BaseModel):
    """ Define como um novo contato a ser inserido deve ser representado
    """
    passageiro_id: int = 1
    telefone: str = "11-9467-3456"
    tipo: str = "Celular"
