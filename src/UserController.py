from flask import Flask, jsonify, request
from User import User
from Validation import validate_email, validate_datetime, validate_length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
users = []

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    #Lepimo podatke iz Json requesta
    name = data['name']
    surname = data['surname']
    username = data['username']
    birth_date = data['birth_date']
    email = data['email']
    password = data['password']

    #Validacija
    if not validate_datetime(birth_date):
        return jsonify({'message': 'Invalid datetime format for birth_date.'}), 400

    if not validate_email(email):
        return jsonify({'message': 'Invalid email format.'}), 400

    if not validate_length(name, 2, 50):
        return jsonify({'message': 'Invalid name length.'}), 400

    if not validate_length(surname, 2, 50):
        return jsonify({'message': 'Invalid surname length.'}), 400

    if not validate_length(username, 2, 50):
        return jsonify({'message': 'Invalid username length.'}), 400

    if not validate_length(email, 6, 50):
        return jsonify({'message': 'Invalid email length.'}), 400

    if not validate_length(password, 6, 50):
        return jsonify({'message': 'Invalid password length.'}), 400

    if any(user.username == username for user in users):
        return jsonify({'message': 'Username is already taken.'}), 400

    #Kreiramo novog usera i saljemo ga na server
    user = User(name, surname, birth_date, username, email, password)
    users.append(user)

    return jsonify({'message': 'User registered successfully!'})

if __name__ == '__main__':
    app.run(debug=True)