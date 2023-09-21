from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at).all()
        message_list = [
            {
                'id': message.id,
                'body': message.body,
                'username': message.username,
                'created_at': message.created_at,
                'updated_at': message.updated_at
            }
            for message in messages
        ]
        return jsonify(message_list)

    elif request.method == 'POST':
        data = request.get_json()
        body = data.get('body')
        username = data.get('username')

        if body and username:
            new_message = Message(body=body, username=username)
            db.session.add(new_message)
            db.session.commit()
            return jsonify({
                'id': new_message.id,
                'body': new_message.body,
                'username': new_message.username,
                'created_at': new_message.created_at,
                'updated_at': new_message.updated_at
            }), 201
        else:
            return jsonify({'error': 'Both body and username are required'}), 400


@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    if request.method == 'PATCH':
        data = request.get_json()
        new_body = data.get('body')

        if new_body:
            message.body = new_body
            db.session.commit()
            return jsonify({
                'id': message.id,
                'body': message.body,
                'username': message.username,
                'created_at': message.created_at,
                'updated_at': message.updated_at
            })
        else:
            return jsonify({'error': 'New body is required for updating'}), 400

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return jsonify({'message': 'Message deleted'})

if __name__ == '__main__':
    app.run(port=5555)
