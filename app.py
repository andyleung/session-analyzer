__author__ = 'aleung@juniper.net'


#
# Copyright (c) 2008 - 2015 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

from flask import Flask, render_template, request, redirect, url_for
from jnpr.junos import Device
import sessionsDAO
import pymongo

app = Flask(__name__)

@app.route('/')
def home():
	return "Hello, world!!"

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
    	hostname = request.form['hostname'] 
        username = request.form['username'] 
        password = request.form['password']
        #
        # Todo: retrieve session information
        #
        dev = Device(hostname,user=username,password=password)
        if dev.open():
            print "Login confirm"
            session_table = dev.rpc.get_flow_session_information()
            status = dev.rpc.get_flow_session_information(summary=True)
            sessions.insert_entry(session_table)
            sessions.insert_device(dev.facts, status)
            ## print session_table
            device = dev.facts
            print "Device Name: ", device['hostname']
            print device
            dev.close()
            return redirect(url_for('welcome'))
        else:
            error = 'Wrong Credentials. Please try again.'
    return render_template('login.html', error=error)

app.secret_key = "juniper"
connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.srx
sessions = sessionsDAO.SessionsDAO(database)


if __name__ == '__main__':
	app.run(debug=True)

