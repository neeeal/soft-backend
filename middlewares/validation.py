import re

class CustomException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
class IncorrectMethodException(CustomException):
    pass

class IncorrectFieldsException(CustomException):
    pass

class IncorrectFormatException(CustomException):
    pass

class IncorrectDataException(CustomException):
    pass

class AccountExistsException(CustomException):
    pass

class InvalidCredentialsException(CustomException):
    pass

class InvalidLoginTokenException(CustomException):
    pass

# class AlreadyLoggedInException(CustomException):
#     def __init__(self, data):
#         self.token = data["token"]
#         self.message = data["message"]
#         self.message = data["message"]
        
def secure_password(password):
    # Password Requirements:
    # at least 8 characters, one lowercase letter, one uppercase letter,
    # one number, and one special character
    if len(password) < 8:
        raise IncorrectDataException("Client Error. Password must be at least 8 characters.")
    if not re.search('[a-z]', password):
        raise IncorrectDataException("Client Error. Password must contain at least 1 lowercase letter.")
    if not re.search('[A-Z]', password):
        raise IncorrectDataException("Client Error. Password must contain at least 1 uppercase letter.")
    if not re.search('[0-9]', password):
        raise IncorrectDataException("Client Error. Password must contain at least 1 number.")
    if not re.search("[@_!#$%^&*()<>?/|}{~:]", password): 
        raise IncorrectDataException("Client Error. Password must contain at least one special character.")
        
    return password

def email_format(email):
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        print(email)
        raise IncorrectDataException("Client Error. Email must be a valid email address.")
    return email

def username_format(username):
    if len(username) < 3:
        raise IncorrectDataException("Client Error. Username must be at least 3 characters.")
    return username

def contact_format(contact):
    if len(contact) != 11:
        raise IncorrectDataException("Client Error. Contact must be 11 digits.")
    if not contact.isnumeric():
        raise IncorrectDataException("Client Error. Contact must only contain numbers.")
    return contact

def is_POST(method):
    if method == 'POST':
        return method
    raise IncorrectMethodException("Client Error. Incorrect method. Should be POST.")

def is_GET(method):
    if method == 'GET':
        return method
    raise IncorrectMethodException("Client Error. Incorrect method. Should be GET.")

def is_DELETE(method):
    if method == 'DELETE':
        return method
    raise IncorrectMethodException("Client Error. Incorrect method. Should be DELETE.")

def is_PUT(method):
    if method == 'PUT':
        return method
    raise IncorrectMethodException("Client Error. Incorrect method. Should be PUT.")

def signup_data(data):
    required_fields = ['first_name', 'last_name', 'contact', 'username', 'password', 'email']
    for field in required_fields:
        if field not in data or len(data[field].strip()) == 0:
            raise IncorrectFieldsException(f"Client Error. Incorrect field: {field} is missing or empty.")

    data['contact'] = contact_format(data['contact'])
    data['username'] = username_format(data['username'])
    data['password'] = secure_password(data['password'])
    data['email'] = email_format(data['email'])

    return data

def login_data(data):
    if "password" not in data or len(data["password"].strip()) == 0:
        raise IncorrectFieldsException("Client Error. Incorrect field: password is missing or empty.")

    if ("user" not in data or len(data["user"].strip()) == 0):
        raise IncorrectFieldsException("Client Error. Incorrect field: username is missing or empty.")

    return data

def image_data(data):
    if "image" not in data and "value" not in data:
        raise IncorrectFieldsException("Client Error. Missing Image Data")
    
    return data