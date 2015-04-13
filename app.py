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

from flask import Flask, render_template, request, redirect, url_for, jsonify
from jnpr.junos import Device
import sessionsDAO
import pymongo
import json

app = Flask(__name__)

# route for handling the SRX login 
@app.route('/')
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

@app.route('/session/destination')
def get_destination():
    data = sessions.top_destination()
    return json.dumps(data)

@app.route('/session/destination_bar', methods=['GET','POST'])
@app.route('/session/destination_bar/<int:limit>', methods=['GET','POST'])
def get_destination_bar(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    data = sessions.top_destination(limit)
    return render_template('bar_chart.html', 
        title = "Top destinations", data=data, labels=[{'x':'count'},{'y':'Destination'}])

@app.route('/session/source')
def get_source():
    data = sessions.top_source()
    return json.dumps(data)

@app.route('/session/source_bar', methods=['GET','POST'])
@app.route('/session/source_bar/<int:limit>', methods=['GET','POST'])
def get_source_bar(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions']   
    data = sessions.top_source(limit)
    return render_template('bar_chart.html', 
        title = "Top sources", data=data, labels=[{'x':'count'},{'y':'Source'}])

@app.route('/session/top_talker', methods=['GET','POST'])
@app.route('/session/top_talker/<int:limit>', methods=['GET','POST'])
def get_talker(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    data = sessions.top_talker(limit)
    return render_template('bar_chart.html', 
        title = "Top Talkers (kbyte)", data=data, labels=[{'x':'count'},{'y':'Source'}])

@app.route('/session/top_pkt', methods=['GET','POST'])
@app.route('/session/top_pkt/<int:limit>', methods=['GET','POST'])
def get_pkt(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    data = sessions.top_pkt(limit)
    return render_template('bar_chart.html', 
        title = "Top Talkers (packets)", data=data, labels=[{'x':'count'},{'y':'Source'}])

@app.route('/session/top_policy', methods=['GET','POST'])
@app.route('/session/top_policy/<int:limit>', methods=['GET','POST'])
def get_policy(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    data = sessions.top_policy(limit)
    return render_template('bar_chart.html', 
        title = "Top Policies", data=data, labels=[{'x':'count'},{'y':'Policy'}])

@app.route('/session/top_source_port', methods=['GET','POST'])
@app.route('/session/top_source_port/<int:limit>', methods=['GET','POST'])
def get_source_port(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    data = sessions.top_source_port(limit)
    return render_template('bar_chart.html', 
        title = "Top Source Ports", data=data, labels=[{'x':'count'},{'y':'Source_Port'}])

@app.route('/session/top_destination_port', methods=['GET','POST'])
@app.route('/session/top_destination_port/<int:limit>', methods=['GET','POST'])
def get_destination_port(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    data = sessions.top_destination_port(limit)
    return render_template('bar_chart.html', 
        title = "Top Destination Ports", data=data, labels=[{'x':'count'},{'y':'Destination_Port'}])

@app.route('/session/top_protocol', methods=['GET','POST'])
@app.route('/session/top_protocol/<int:limit>', methods=['GET','POST'])
def get_protocol(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    data = sessions.top_protocol(limit)
    return render_template('bar_chart.html', 
        title = "Top Protocols", data=data, labels=[{'x':'count'},{'y':'Protocol'}])

@app.route('/device_info')
def get_device():
    data = sessions.get_attributes()
    print data
    return render_template('device.html', data=data)

app.secret_key = "juniper"
connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.srx
sessions = sessionsDAO.SessionsDAO(database)


if __name__ == '__main__':
	app.run( host='0.0.0.0', port=5000, debug=True)



