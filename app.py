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
from lxml import etree
import sessionsDAO
import pymongo
import json

app = Flask(__name__)

# route for handling the SRX login 
@app.route('/', methods=['GET','POST'])
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
            print "Login success"
            session_table = dev.rpc.get_flow_session_information()
            status = dev.rpc.get_flow_session_information(summary=True)
            sessions.insert_entry(session_table)
            sessions.insert_device(dev.facts, status)
            ## print session_table
            device = dev.facts
            print "Device Name: ", device['hostname']
            print device
            dev.close()
            return redirect(url_for('get_device'))
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
        title = "Top Talkers (bytes)", data=data, labels=[{'x':'count'},{'y':'Source'}])

@app.route('/session/top_pkt', methods=['GET','POST'])
@app.route('/session/top_pkt/<int:limit>', methods=['GET','POST'])
def get_pkt(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    data = sessions.top_pkt(limit)
    return render_template('bar_chart.html', 
        title = "Top Talkers (packets)", data=data, labels=[{'x':'count'},{'y':'Source'}])

@app.route('/session/top_ingress', methods=['GET','POST'])
@app.route('/session/top_ingress/<int:limit>', methods=['GET','POST'])
def get_ingress(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    data = sessions.top_ingress(limit)
    return render_template('bar_chart.html', 
        title = "Top Ingress Ports (bytes)", data=data, labels=[{'x':'count'},{'y':'Ingress'}])

@app.route('/session/top_egress', methods=['GET','POST'])
@app.route('/session/top_egress/<int:limit>', methods=['GET','POST'])
def get_egress(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    data = sessions.top_egress(limit)
    return render_template('bar_chart.html', 
        title = "Top Egress Ports (bytes)", data=data, labels=[{'x':'count'},{'y':'Egress'}])

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

@app.route('/session/top_country', methods=['GET','POST'])
@app.route('/session/top_country/<int:limit>', methods=['GET','POST'])
def get_country(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    result = sessions.top_country(limit)
    ## print "Country data: ", data
    data = []
    for i in result:
        if i['Country']:
            data.append(i)
    return render_template('bar_chart.html', 
        title = "Top Countries", data=data, labels=[{'x':'count'},{'y':'Country'}])

@app.route('/session/top_city', methods=['GET','POST'])
@app.route('/session/top_city/<int:limit>', methods=['GET','POST'])
def get_city(limit=10):
    if request.method == 'POST':
        limit = request.form['num_of_sessions'] 
    result = sessions.top_city(limit)
    data = []
    for i in result:
        if i['City']:
            data.append(i)
    return render_template('bar_chart.html', 
        title = "Top Cities", data=data, labels=[{'x':'count'},{'y':'City'}])

@app.route('/map')
def draw_map():
    scale = 100
    limit = 100
    # Sample ip_info = [{'count':100, 'latitude': 37.385999999999996, 'ip': '8.8.8.8', 'longitude': -122.0838}, 
    ip_info = sessions.top_country(limit)
    # print "IP info: ", ip_info
    list_of_countries = []
    for i in ip_info:
         if i['Country']:
              #print "country: ", i['Country']
              list_of_countries.append(i)
    return render_template('map.html', info=list_of_countries, max=scale)  # render a template

@app.route('/map3')
def draw_map3():
    limit = 100
    # Sample ip_info = [{'count':100, 'latitude': 37.385999999999996, 'ip': '8.8.8.8', 'longitude': -122.0838}, 
    ip_info = sessions.top_country(limit)
    # print "IP info: ", ip_info
    data = []
    for i in ip_info:
         if i['Country']:
              #print "country: ", i['Country']
              i['radius'] = 12
              i['fillKey'] ='bubbleEX'
              data.append(i)
    return render_template('map3.html', data=data)  # render a template


@app.route('/table/top_talker', methods=['GET','POST'])
def get_talker_all():
    if request.method == 'POST':
        ip = request.form['ip_address']
        byte_table = sessions.detail_ip_byte(ip)
        session_table = sessions.detail_ip_session(ip)
        print "Volume Details: ", byte_table
        print "Session Details: ", session_table
        data = []
        for x,y in zip(byte_table, session_table):
            z = x.copy()
            z.update(y)
            data.append(z)
        return render_template('session_details.html',title = "Top Talker Details: ",ip=ip, data=data)
    data = sessions.top_talker_all()
    print "Top Talkers: ", data
    return render_template('sessions.html', 
        title = "Top Talkers (bytes)", data=data)


@app.route('/device_info')
def get_device():
    data = sessions.get_attributes()
    return render_template('device.html', data=data)

@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    elif request.method == 'POST':
        # Get the name of the uploaded file
        file = request.files['file']
        # Check if the file is one of the allowed types/extensions
        if file: 
            tree = etree.parse(file)
            root = tree.getroot()
            sessions.insert_entry(root)
    ## return render_template('upload.html')
    return redirect(url_for('draw_map3'))


app.secret_key = "juniper"
connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.srx
sessions = sessionsDAO.SessionsDAO(database)


if __name__ == '__main__':
	app.run( host='0.0.0.0', port=5000, debug=True)



