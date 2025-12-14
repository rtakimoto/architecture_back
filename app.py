from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, request, jsonify
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from models import Session, Passageiro, Contato
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
passageiro_tag = Tag(name="Passageiro", description="Adição, visualização, atualização e remoção de passageiros à base")
contato_tag = Tag(name="Contato", description="Adição de um contato a um passageiro cadastrado na base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/passageiro', tags=[passageiro_tag], 
          responses={"200": PassageiroViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_passageiro(body:PassageiroSchema): 
    """Adiciona um novo Passageiro à base de dados

    Retorna uma representação dos passageiros e contatos associados.
    """

    data= request.get_json();    
    passageiro = Passageiro(
        nome=data.get("nome"),
        cpf=data.get("cpf"),
        birthdate=data.get("birthdate"),
        flight=data.get("flight")
    )

    
    try:
        # criando conexão com a base
        session = Session()
        # adicionando produto
        session.add(passageiro)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado passageiro de nome e cpf: '{passageiro.nome}', '{passageiro.cpf}'")
        return apresenta_passageiro(passageiro), 200

    except IntegrityError as e:
        # como a duplicidade de cpf é a provável razão do IntegrityError
        error_msg = "Passageiro de mesmo cpf já salvo na base :/"
        logger.warning(f"Erro ao adicionar passageiro:'{passageiro.nome}', '{passageiro.cpf}', {error_msg}")
        return {"message": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar passageiro '{passageiro.nome}', '{passageiro.cpf}', {error_msg}")
        return {"message": error_msg}, 400


@app.get('/passageiros', tags=[passageiro_tag],
         responses={"200": ListagemPassageirosSchema, "404": ErrorSchema})
def get_passageiros():
    """Faz a busca por todos os Passageiros cadastrados

    Retorna uma representação da listagem de passageiros.
    """
    logger.debug(f"Coletando passageiros ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    passageiros = session.query(Passageiro).all()

    if not passageiros:
        # se não há passageiros cadastrados
        return {"passageiros": []}, 200
    else:
        logger.debug(f"%d passageiros econtrados" % len(passageiros))
        # retorna a representação de passageiro
        print(passageiros)
        return apresenta_passageiros(passageiros), 200


@app.get('/passageiro', tags=[passageiro_tag],
         responses={"200": PassageiroViewSchema, "404": ErrorSchema})
def get_passageiro(query: PassageiroBuscaSchema):
    """Faz a busca por um Passageiro a partir do CPF do passageiro

    Retorna uma representação dos passageiros e contatos associados.
    """
    passageiro_cpf = query.cpf
    logger.debug(f"Coletando dados sobre passageiro #{passageiro_cpf}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    passageiro = session.query(Passageiro).filter(Passageiro.cpf == passageiro_cpf).first()

    if not passageiro:
        # se o passageiro não foi encontrado
        error_msg = "Passageiro não encontrado na base :/"
        logger.warning(f"Erro ao buscar passageiro '{passageiro_cpf}', {error_msg}")
        return {"message": error_msg}, 404
    else:
        logger.debug(f"Passageiro econtrado: '{passageiro.cpf}'")
        # retorna a representação de passageiro
        return apresenta_passageiro(passageiro), 200

@app.put('/passageiro', tags=[passageiro_tag],
            responses={"200": PassageiroViewSchema, "404": ErrorSchema})
def update_passageiro(body:PassageiroUpdateSchema): 
    """Atualiza um Passageiro a partir do id de passageiro informado

    Retorna uma mensagem de confirmação da atualização.
    """
    data= request.get_json();
    
    passageiro_id  = data.get("id")
    passageiro_nome  = data.get("nome")
    passageiro_cpf  = data.get("cpf")
    passageiro_birthdate = data.get("birthdate")
    passageiro_flight  = data.get("flight")
    
    logger.debug(f"Atualizando passageiro de cpf: '{passageiro_cpf}'")
    # criando conexão com a base
    session = Session()
    # fazendo a atualizacao
    count = session.query(Passageiro).filter(Passageiro.id == passageiro_id).update({'nome': passageiro_nome, 'cpf': passageiro_cpf, 'flight': passageiro_flight})
    session.commit()
    # fazendo a busca
    passageiro = session.query(Passageiro).filter(Passageiro.id == passageiro_id).first()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Atualizado passageiro #{passageiro_id}")
        return apresenta_passageiro(passageiro), 200
    else:
        # se o passageiro não foi encontrado
        error_msg = "Passageiro não encontrado na base :/"
        logger.warning(f"Erro ao atualizar passageiro #'{passageiro_id}', {error_msg}")
        return {"message": error_msg}, 404

@app.delete('/passageiro', tags=[passageiro_tag],
            responses={"200": PassageiroDelSchema, "404": ErrorSchema})
def del_passageiro(query: PassageiroBuscaSchema):
    """Deleta um Passageiro a partir do cpf do passageiro informado

    Retorna uma mensagem de confirmação da remoção.
    """
    passageiro_cpf = unquote(unquote(query.cpf))
    print(passageiro_cpf)
    logger.debug(f"Deletando dados sobre passageiro #{passageiro_cpf}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Passageiro).filter(Passageiro.cpf == passageiro_cpf).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado passageiro #{passageiro_cpf}")
        return {"message": "Passageiro removido", "id": passageiro_cpf}
    else:
        # se o passageiro não foi encontrado
        error_msg = "Passageiro não encontrado na base :/"
        logger.warning(f"Erro ao deletar passageiro #'{passageiro_cpf}', {error_msg}")
        return {"message": error_msg}, 404


@app.post('/contato', tags=[contato_tag],
          responses={"200": PassageiroViewSchema, "404": ErrorSchema})
def add_contato(body:ContatoSchema): 
    """Adiciona de um novo contato a um passageiro cadastrado na base identificado pelo id

    Retorna uma representação dos passageiros e contatos associados.
    """
    data= request.get_json();
    
    passageiro_id  = data.get("passageiro_id")

    logger.debug(f"Adicionando contato ao passageiro #{passageiro_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca pelo passageiro
    passageiro = session.query(Passageiro).filter(Passageiro.id == passageiro_id).first()

    if not passageiro:
        # se passageiro não encontrado
        error_msg = "Passageiro não encontrado na base :/"
        logger.warning(f"Erro ao adicionar contato ao passageiro '{passageiro_id}', {error_msg}")
        return {"message": error_msg}, 404

    # criando o contato
    contato = Contato(
        telefone=data.get("telefone"),
        tipo=data.get("tipo"))

    # adicionando o contato ao passageiro
    passageiro.adiciona_contato(contato)
    session.commit()

    logger.debug(f"Adicionado contato ao passageiro #{passageiro_id}")

    # retorna a representação de passageiro
    return apresenta_passageiro(passageiro), 200
