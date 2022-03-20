


import os
from datetime import datetime
from flask import Flask, Response, json, request
from pymongo import MongoClient
import constants


app = Flask(__name__)

os.environ['DATABASE_URL'] = constants.DATABASE_URL
os.environ['DATABASE_NAME'] = constants.DATABASE_NAME
os.environ['SSHLOGINS_COLLECTION'] = constants.SSH_LOGIN_COLLECTION

@app.route("/",methods=['GET'])
def get_login_count():

    # We are passing the date here as a query parameter
    check_default = request.args['date']
    date = check_default.lower()

    try:
        # Connecting to the pymongo client
        client = MongoClient(os.environ.get('DATABASE_URL'))
        mydb = client[os.environ.get('DATABASE_NAME')]
        ssh_attempt_logins = mydb[os.environ.get('SSHLOGINS_COLLECTION')]
        ssh_attempt_logins =  ssh_attempt_logins.find()
        ssh_attempt_logins = [item for item in ssh_attempt_logins]
        ssh_attempt_logins = ssh_attempt_logins[0][date]

    except Exception as error:
        print(f"Error in fetching the details of the ssh login attempts for the given day - {error}")
        return Response(mimetype="application/json", response=json.dumps(f"Error in fetching the details of the ssh login attempts for the given day - {error}"),status=500)
    else:
        return Response(mimetype="application/json", response=json.dumps(ssh_attempt_logins),status=200)


if __name__ == "__main__":
    app.run()