#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, url_for
from flask.ext.httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
app = Flask(__name__)

heros = [
    {
        'id': 1,
        'name': u'Iron Man',
        'description': u'Iron Man (Tony Stark) is a fictional superhero appearing in American comic books published by Marvel Comics.', 
        'done': False
    },
    {
        'id': 2,
        'name': u'Batman',
        'description': u'Batman is a fictional superhero appearing in American comic books published by DC Comics.', 
        'done': False
    }
]

#Rota de entrada da API
@app.route('/')
def index():
    return "IT'S WORKING!"

#Lista todos herois
#Rota com autenticacao
@app.route('/hero/api/v1/heros', methods=['GET'])
@auth.login_required
def get_heros():
    return jsonify({'heros': [make_public_hero(hero) for hero in heros]}, 403)

#Detalhes de um heroi passando hero_id
@app.route('/hero/api/v1/heros/<int:hero_id>', methods=['GET'])
def get_hero(hero_id):
    hero = [hero for hero in heros if hero['id'] == hero_id]
    if len(hero) == 0:
        abort(404)
    return jsonify({'hero': hero[0]})

#Insere novo heroi
@app.route('/hero/api/v1/heros', methods=['POST'])
def create_hero():
    if not request.json or not 'name' in request.json:
        abort(400)
    hero = {
        'id': heros[-1]['id'] + 1,
        'name': request.json['name'],
        'description': request.json.get('description', ""),
        'done': False
    }
    heros.append(hero)
    return jsonify({'hero': hero}), 201

#Atualiza heroi
@app.route('/hero/api/v1/heros/<int:hero_id>', methods=['PUT'])
def update_hero(hero_id):
    hero = [hero for hero in heros if hero['id'] == hero_id]
    if len(hero) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    hero[0]['name'] = request.json.get('name', hero[0]['name'])
    hero[0]['description'] = request.json.get('description', hero[0]['description'])
    hero[0]['done'] = request.json.get('done', hero[0]['done'])
    return jsonify({'hero': hero[0]})

#Deleta heroi
@app.route('/hero/api/v1/heros/<int:hero_id>', methods=['DELETE'])
def delete_hero(hero_id):
    hero = [hero for hero in heros if hero['id'] == hero_id]
    if len(hero) == 0:
        abort(404)
    heros.remove(hero[0])
    return jsonify({'result': True})

#Criar url para retornar na lista de herois ao inves de retornar id
def make_public_hero(hero):
    new_hero = {}
    for field in hero:
        if field == 'id':
            new_hero['uri'] = url_for('get_hero', hero_id=hero['id'], _external=True)
        else:
            new_hero[field] = hero[field]
    return new_hero

#middleware para autenticacao de rotas
@auth.get_password
def get_password(username):
    if username == 'api_user':
        return 'python'
    return None

#middleware para erro de acesso nao autorizado
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

#middleware para erro de rota nao encontrada
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)