from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, request, jsonify
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from models import Session, Passageiro, Contato
from logger import logger
from schemas import *
from datetime import datetime
from flask_cors import CORS

import requests

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
passageiro_tag = Tag(name="Passageiro", description="Adição, visualização, atualização e remoção de passageiros à base")
contato_tag = Tag(name="Contato", description="Adição de um contato a um passageiro cadastrado na base")
external_tag = Tag(name="API Externa", description="Acesso às APIs externas")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

# Endpoint to validate CPF
@app.get("/external-data", tags=[external_tag],
         responses={"200": RetornaCPFSchema, "404": ErrorSchema})
def get_external_data(query: CPFValidaSchema):
    """
    Calls an external API and returns the JSON response.
    Example: /external-data?cpf=71454597011&birthdate=1935-12-04
    """
    cpf = query.cpf
    birthdate = query.birthdate

    # Validate input
    if not cpf:
        return jsonify({"error": "Missing 'cpf' query parameter"}), 400

    if not birthdate:
        return jsonify({"error": "Missing 'birthdate' query parameter"}), 400

    try:
        # External API 
        api_key = "MpYLNaIH8agztz_PuGF0wuAX3AhU4D8souCpTdCk"
        url = f"https://api.infosimples.com/api/v2/consultas/receita-federal/cpf?token={api_key}&cpf={cpf}&birthdate={birthdate}"

        response = requests.post(url, timeout=5)
        response.raise_for_status()  # Raise HTTPError for bad responses

        data = response.json()
        code = data.get("code") #612 - nao encontrado, 608 - nascimento divergente do cpf, 603 - bloqueado, 200 - ok
        count = data.get("data_count")
        
        if count == 0:
            # Return only relevant fields
            result = {
                "code": code, #612 - nao encontrado, 608 - nascimento divergente do cpf, 200 - ok
                "count": count,
                "nome": "",
                "situacao": ""
            } 
        else:
            # Return only relevant fields
            result = {
                "code": code, #612 - nao encontrado, 608 - nascimento divergente do cpf, 200 - ok
                "count": count,
                "nome": data.get("data", [{}])[0].get("nome"),
                "situacao": data.get("data", [{}])[0].get("situacao_cadastral")
            }

        return jsonify(result)

    except requests.exceptions.Timeout:
        return jsonify({"error": "External API request timed out"}), 504
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"External API error: {e}"}), 502
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.post('/passageiro', tags=[passageiro_tag], 
          responses={"200": PassageiroViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_passageiro(body:PassageiroSchema): 
    """Adiciona um novo Passageiro à base de dados

    Retorna uma representação dos passageiros e contatos associados.
    """

    data= request.get_json();    
    input_date = data.get("birthdate");
    dt = datetime.strptime(input_date, "%Y-%m-%dT%H:%M:%S");
    passageiro = Passageiro(
        nome=data.get("nome"),
        cpf=data.get("cpf"),
        birthdate=dt,
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
        logger.debug(f"%d passageiros encontrados" % len(passageiros))
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
    input_date = data.get("birthdate");
    dt = datetime.strptime(input_date, "%Y-%m-%dT%H:%M:%S");
    
    passageiro_id  = data.get("id")
    passageiro_nome  = data.get("nome")
    passageiro_cpf  = data.get("cpf")
    passageiro_birthdate = dt
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
