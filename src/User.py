from datetime import datetime

class User:
    def __init__(self, name, surname, birth_date, username, email, password):
        self.name = name
        self.surname = surname
        self.birth_date = birth_date
        self.username = username
        self.email = email
        self.password = password
