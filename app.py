from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId  # Import ObjectId to convert ObjectId to string
from urllib.parse import quote_plus

app = Flask(__name__)

# Enable CORS for all origins
CORS(app)

# MongoDB connection setup
username = 'pradeeprm2310'
password = 'Pradeep@2310'
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

client = MongoClient(
    f'mongodb+srv://{encoded_username}:{encoded_password}@cluster0.twfffwi.mongodb.net/MYDB?retryWrites=true&w=majority&appName=Cluster0')
db = client['MYDB']
collection = db['users']
char_db = db['characters']
@app.route('/')
def index():
    return 'Server is running'

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    if not all([first_name, last_name, email, password]):
        return jsonify({'error': 'Incomplete data'}), 400

    user = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password
    }
    collection.insert_one(user)
    return jsonify({'success': True}), 201
@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({'error': 'Incomplete data'}), 400

    user = collection.find_one({"email": email, "password": password})
    if user:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/users', methods=['GET'])
def get_users():
    users = collection.find()
    users_list = []
    for user in users:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        users_list.append(user)
    print(users_list)
    return jsonify({'users': users_list}), 200
@app.route('/characters', methods=['POST'])
def add_character():
    data = request.json
    name = data.get("name")
    image = data.get("image")
    description = data.get("description")
    quotes = data.get("quotes")
    abilities = data.get("abilities")

    if not all([name, image, description]):
        return jsonify({'error': 'Incomplete data'}), 400

    character = {
        "name": name,
        "image": image,
        "description": description,
        "quotes": quotes,
        "abilities": abilities
    }
    print(character)
    inserted_character = char_db.insert_one(character)
    return jsonify({
        'success': True,
        'id': str(inserted_character.inserted_id)  # Convert ObjectId to string
    }), 201
@app.route('/characters', methods=['GET'])
def get_characters():
    characters = list(char_db.find())  # Convert cursor to list of dictionaries
    for character in characters:
        character['_id'] = str(character['_id'])  # Convert ObjectId to string
    return jsonify(characters), 200
@app.route('/characters/<string:id>', methods=['DELETE'])
def delete_character(id):
    result = char_db.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Character not found'}), 404
@app.route('/characters/<string:id>', methods=['PUT'])
def update_character(id):
    data = request.json
    name = data.get("name")
    image = data.get("image")
    description = data.get("description")
    quotes = data.get("quotes")
    abilities = data.get("abilities")

    # Check if all required fields are present
    if not all([name, image, description]):
        return jsonify({'error': 'Incomplete data'}), 400

    # Update the character in MongoDB
    result = char_db.update_one(
        {'_id': ObjectId(id)},
        {'$set': {
            'name': name,
            'image': image,
            'description': description,
            'quotes': quotes,
            'abilities': abilities
        }}
    )

    if result.modified_count == 1:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Character not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
