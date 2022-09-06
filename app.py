import os
import sys

relative = "../"
sys.path.insert(1, str(os.path.abspath(relative)))
import datetime

import pytz
import re
import logging
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
import configparser

secret_key = b'gslabflaskAssign@123'
from auth import auth
config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__, template_folder=config.get('constants', 'template_folder'))
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('constants', 'db_url')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
email_regex = config.get('constants', 'email_regex')
log_files = r'./logs/' + str(
    datetime.datetime.now().strftime("%d-%b-%Y %H-%M-%S")) + ".log"
logger = logging.getLogger()


class employees(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    datecreated = db.Column(db.DateTime())

    def __repr__(self):
        return '<emp %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
@auth.login_required
def index():
    if request.method == 'POST':
        a_first_name = request.form['firstname']
        a_last_name = request.form['lastname']
        a_email = request.form['email']


        if re.fullmatch(email_regex, a_email):
            tz = pytz.timezone('Asia/Kolkata')
            a_datecreated = datetime.datetime.now().astimezone(tz)
            new_emp = employees(first_name=a_first_name, last_name=a_last_name, email=a_email,
                                datecreated=a_datecreated)
            try:
                db.session.add(new_emp)
                db.session.flush()
                logger.info(f'{a_email} user added')
                return redirect('/')
            except Exception as e:
                db.session.rollback()
                if 'sqlite3.IntegrityError' in str(e):
                    logger.info(f'Exception : "Duplicate issue editing employee :"{str(e)}')
                    return {
                        "DuplicateEmailError": "Employee Already Exist",
                    }
                else:
                    logger.info(f'Exception : "Some issue editing employee :"{str(e)}')
                    return ' There was an Error while editing'
            finally:
                db.session.commit()
    else:
        emps = employees.query.all()
        return render_template("home.html", emps=emps)


@app.route('/add', methods=['GET'])
@auth.login_required
def add_page():
    return render_template("addpage.html")


@app.route('/delete/<int:id>')
@auth.login_required
def delete(id):
    emp_to_delete = employees.query.get_or_404(id)
    try:
        db.session.delete(emp_to_delete)
        db.session.flush()
        logger.info(f'Deleted employee :" +{str(emp_to_delete)}')
        return redirect('/')
    except Exception as e:
        db.session.rollback()
        logger.info(f'Exception : "there was an issue deleting employee :"{str(e)}')
        return "there was a problem"
    finally:
        db.session.commit()


@app.route('/edit/<int:id>', methods=['POST', 'GET'])
@auth.login_required
def edit_func(id):
    if request.method == 'POST':
        a_first_name = request.form['firstname']
        a_last_name = request.form['lastname']
        a_email = request.form['email']

        if re.fullmatch(email_regex, a_email):
            tz = pytz.timezone('Asia/Kolkata')
            employees.query.filter_by(id=id).update(
                dict(first_name=a_first_name, last_name=a_last_name, email=a_email))
            try:
                db.session.flush()
                logger.info(f'Edited employee :" {str(a_email)}')
                return redirect('/')
            except Exception as e:
                db.session.rollback()
                if('sqlite3.IntegrityError' in str(e)):
                    logger.info(f'Exception : "Duplicate issue editing employee :"{str(e)}')
                    return {
                        "DuplicateEmailError": "Employee Already Exist",
                    }
                else:
                    logger.info(f'Exception : "Some issue editing employee :"{str(e)}')
                    return ' There was an Error while editing'

            finally:
                db.session.commit()

        else:
            return {
                "EmailValidationError": "Please Provide a Valid Email Address",
            }
    elif request.method == 'GET':
        emp_edit = employees.query.filter_by(id=id).first()
        return render_template("editPage.html", emp=emp_edit)


if __name__ == '__main__':
    logformat = config.get('constants', 'log_format', raw=True)
    datefmt = "%m-%d-%Y %H:%M"
    logging.basicConfig(filename=log_files, level=logging.DEBUG, filemode="w", format=logformat, datefmt=datefmt)
    handler = logging.StreamHandler(sys.stdout)
    handler = RotatingFileHandler(log_files, mode='a', maxBytes=8 * 1024, encoding=None, delay=0)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.info('Flask App Started')
    app.run(host='127.0.0.1', port='3000', debug=False)
