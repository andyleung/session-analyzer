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

import sys
import pygeoip
from cgi import escape
from bson.son import SON
from datetime import datetime

# The Blog Post Data Access Object handles interactions with the Posts collection
class SessionsDAO:

    # constructor for the class
    def __init__(self, database):
        self.db = database
        self.sessions = database.sessions
        self.device = database.device

    # inserts the blog entry and returns a permalink for the entry
    def insert_entry(self, session_table):
        print "inserting session table ..."
        self.sessions.drop()
        geodata = pygeoip.GeoIP('static/GeoLiteCity.dat')

        for session in session_table.findall('.//flow-session'):
            id = session.find('session-identifier')
            policy = session.findtext('policy')
            app_name = session.find('application-name')
            app_value = session.find('application-value')
            if app_name is not None:
                application_name = app_name.text
            else:
                application_name = ""
            if app_value is not None:
                application_value = int(app_value.text)
            else:
                application_value = ""

            pkt = session.findall('flow-information/pkt-cnt')  
            pkt_cnt = int(pkt[0].text) + int(pkt[1].text)
            bytes = session.findall('flow-information/byte-cnt')  
            byte_cnt = int(bytes[0].text) + int(bytes[1].text)
            source = session.findtext('flow-information/source-address')
            source_port = session.findtext('flow-information/source-port')
            destination = session.findtext('flow-information/destination-address')
            destination_port = session.findtext('flow-information/destination-port')
            protocol = session.findtext('flow-information/protocol')
            interfaces = session.findall('flow-information/interface-name')
            ingress = interfaces[0].text
            egress = interfaces[1].text

            # Get Geo info from IP address
            data = geodata.record_by_name(destination.replace('\n',''))
            # debug:
            if data:
                print "Data is: ", data
                country = data['country_name']
                city = data['city']
                longitude = data['longitude']
                latitude = data['latitude']
            else: 
                country = ""
                city = ""
                longitude = ""
                latitude = ""

            # new session entry
            flow = {"session_id": int(id.text),
                     "policy": policy.replace('\n',''),
                     "application_name": application_name.replace('\n',''),
                     "application_value": application_value,                 
                     "pkt_cnt": pkt_cnt,
                     "byte_cnt": byte_cnt,
                     "source": source.replace('\n',''),
                     "source_port": source_port.replace('\n',''),
                     "destination": destination.replace('\n',''),
                     "destination_port": destination_port.replace('\n',''),
                     "protocol": protocol.replace('\n',''),
                     "ingress": ingress.replace('\n',''),
                     "egress": egress.replace('\n',''),
                     "city": city,
                     "country": country,
                     "longitude": longitude,
                     "latitude": latitude
                     }

            # Insert to MongoDB
            try:
                self.sessions.insert(flow)
                ##print "Inserting the session"
            except:
                print "Error inserting post"
                print "Unexpected error:", sys.exc_info()[0]

        print "Done inserting sessions ..."
        return True

    def insert_device(self, device, status):
        print "inserting device info ... "

        unicast_sessions = 0
        multicast_sessions = 0
        failed_sessions = 0
        max_sessions = 0

        #get to the root of the flow tree
        session = status.getparent()[1]
        failed_sessions = session.findtext('failed-sessions')
        max_sessions = session.findtext('max-sessions')
        unicast_sessions = session.findtext('active-unicast-sessions')
        multicast_sessions = session.findtext('active-multicast-sessions')  
        
        # Build a new session entry
        device_info = {
                "hostname": device['hostname'],
                "version": device['version'],
                "serialnumber": device['serialnumber'],
                "model": device['model'],
                "up_time": device['RE0']['up_time'],
                "category":device['personality'],
                "unicast_sessions": unicast_sessions.replace('\n',''),
                "multicast_sessions": multicast_sessions.replace('\n',''),
                "failed_sessions": failed_sessions.replace('\n',''),
                "max_sessions": max_sessions.replace('\n',''),
                "last_update": str(datetime.now())
                }

        # now insert the post
        try:
            self.device.drop()
            self.device.insert(device_info)
            print "Insert the device info successful!!"
        except:
            print "Error inserting post"
            print "Unexpected error:", sys.exc_info()[0]

        return True

    def top_destination(self,limit=10):
        ## pipeline = [{"$group":{"_id":"$destination","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Destination":"$_id","count":1}}]            
        pipeline = [{"$group":{"_id":"$destination","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Destination":"$_id","count":1}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']   
        return data

    def top_source(self,limit=10):
        pipeline = [{"$group":{"_id":"$source","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Source":"$_id","count":1}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']   
        return data

    def top_talker(self,limit=10):
        pipeline = [{"$group":{"_id":"$source","count":{"$sum":"$byte_cnt"}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Source":"$_id","count":1}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']   
        return data

    def top_policy(self,limit=10):
        pipeline = [{"$group":{"_id":"$policy","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Policy":"$_id","count":1}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']  
        return data

    def top_pkt(self,limit=10):
        pipeline = [{"$group":{"_id":"$source","count":{"$sum":"$pkt_cnt"}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Source":"$_id","count":1}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']  
        return data

    def top_ingress(self,limit=10):
        pipeline = [{"$group":{"_id":"$ingress","count":{"$sum":"$byte_cnt"}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Ingress":"$_id","count":1}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']   
        return data

    def top_egress(self,limit=10):
        pipeline = [{"$group":{"_id":"$egress","count":{"$sum":"$byte_cnt"}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Egress":"$_id","count":1}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']   
        return data

    def top_source_port(self,limit=10):
        pipeline = [{"$group":{"_id":"$source_port","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Source_Port":"$_id","count":1}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']  
        return data

    def top_destination_port(self,limit=10):
        pipeline = [{"$group":{"_id":"$destination_port","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Destination_Port":"$_id","count":1}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']  
        return data

    def top_protocol(self,limit=10):
        pipeline = [{"$group":{"_id":"$protocol","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Protocol":"$_id","count":1}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']  
        return data

    def top_country(self, limit=10):
        pipeline = [{"$group":{"_id":{"country":"$country","latitude":"$latitude","longitude":"$longitude"},"count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"Country":"$_id.country","count":1,"latitude":"$_id.latitude","longitude":"$_id.longitude"}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']  
        return data

    def top_city(self, limit=10):
        pipeline = [{"$group":{"_id":"$city","count":{"$sum":1}}},{"$sort":SON([("count",-1)])},{"$project":{"_id":0,"City":"$_id","count":1}},{"$limit":int(limit)}]            
        data = self.sessions.aggregate(pipeline)['result']  
        return data

    def get_attributes(self):
        data = self.device.find_one()
        return data

