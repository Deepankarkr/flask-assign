users = {
    "emp":"Adm@123"
}

from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None
