import os
import sys

relative = "../"
sys.path.insert(1, str(os.path.abspath(relative)))
import datetime

import pytz
import re

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

import configparser
from helper import setup_logger

secret_key = b'flaskAssign@123'
from auth import auth

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__, template_folder=config.get('constants', 'template_folder'))
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('constants', 'db_url')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

email_regex = config.get('constants', 'email_regex')


class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    datecreated = db.Column(db.DateTime())

    def __repr__(self):
        return '<emp %r>' % self.id


@app.route('/', methods=['GET'])
@auth.login_required
def index():
    return redirect("/employee/", code=302)


@app.route('/employee/', methods=['GET'])
@auth.login_required
def home_page():
    if request.method == 'GET':
        emps = Employees.query.all()
        # In case you want the response in JSON
        # cols = ['id','first_name', 'last_name', 'email']
        # result = [{col: getattr(d, col) for col in cols} for d in emps]
        # return(result)
        return render_template("home.html", emps=emps)


@app.route('/employee/add_employee/', methods=['POST', 'GET'])
@auth.login_required
def add_employee_page():
    if request.method == 'GET':
        return render_template("addpage.html")
    elif request.method == 'POST':
        first_name_req = request.form['firstname']
        last_name_req = request.form['lastname']
        email_req = request.form['email']

        if re.fullmatch(email_regex, email_req):
            tz = pytz.timezone('Asia/Kolkata')
            a_datecreated = datetime.datetime.now().astimezone(tz)
            new_emp = Employees(first_name=first_name_req, last_name=last_name_req, email=email_req,
                                datecreated=a_datecreated)
            try:
                db.session.add(new_emp)
                db.session.flush()
                logger.info(f'{email_req} user added')
                return redirect('/')
            except Exception as exception_msg:
                db.session.rollback()
                resp = duplicate_email_exception(str(exception_msg))
                return resp
            finally:
                db.session.commit()
                db.engine.dispose()


@app.route('/employee/delete_employee/<int:id>/')
@auth.login_required
def delete_employee_page(id: int):
    emp_to_delete = Employees.query.get_or_404(id)
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
        db.engine.dispose()


@app.route('/employee/edit_employee/<int:id>/', methods=['POST', 'GET'])
@auth.login_required
def edit_employee_page(id: int):
    if request.method == 'POST':
        try:
            first_name_req = request.form['firstname']
            last_name_req = request.form['lastname']
            email_req = request.form['email']

            if re.fullmatch(email_regex, email_req):
                tz = pytz.timezone('Asia/Kolkata')
                Employees.query.filter_by(id=id).update(
                    dict(first_name=first_name_req, last_name=last_name_req, email=email_req))
                try:
                    db.session.flush()
                    logger.info(f'Edited employee :" {str(email_req)}')
                    return redirect('/')
                except Exception as exception_msg:
                    db.session.rollback()
                    resp = duplicate_email_exception(str(exception_msg))
                    return resp
                finally:
                    db.session.commit()
                    db.engine.dispose()
            else:
                return {
                    "EmailValidationError": "Please Provide a Valid Email Address",
                }
        except Exception as e:
            return {
                "Error": "Issue Processing Editing",
            }
    elif request.method == 'GET':
        try:
            emp_edit = Employees.query.filter_by(id=id).first()
            return render_template("editPage.html", emp=emp_edit)
        except Exception as e:
            return {
                "Error": "Issue fetching information for Exisiting Employee",
            }


def duplicate_email_exception(exception: str):
    try:
        if 'sqlite3.IntegrityError' in str(exception):
            logger.info(f'Exception : "Duplicate issue editing employee :"{str(exception)}')
            return {
                "DuplicateEmailError": "Employee Already Exist",
            }
        else:
            logger.info(f'Exception : "Some issue editing employee :"{str(exception)}')
            return ' There was an Error while editing'
    except Exception as e:
        logger.info(f'Exception : "Some issue editing employee :"{str(e)}')


if __name__ == '__main__':
    try:
        logger = setup_logger()
        app.run(host='127.0.0.1', port='3000', debug=True)
        logger.info('Flask App Started')
    except Exception as e:
        logger.info('Issue starting the Flask Application')
