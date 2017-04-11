#planning to encrypt and decrypt the messages here only in the classes Message and UnMessage

import time
import json

# message types
SIGNIN = 'SIGN-IN'
LIST = 'LIST'
MESSAGE = 'MESSAGE'
EXIT = 'EXIT'


class Message():

    def __init__(self, _type,username,msg=None):

        self.type = _type
        self.msg = msg
        self.time = time.time()
        self.username=username
        self.json = json.dumps(
            {'type': self.type,'username': self.username, 'msg': self.msg, 'time': self.time})

class UnMessage():
    
    def __init__(self,data):
        self.json = json.loads(data)
        self.type = self.json['type']
        self.msg = self.json['msg']
        self.time = self.json['time']
        self.username=self.json['username']
        

    def get_message(self):
        return self.msg
    
    def get_type(self):
        return self.type
    
    def get_time(self):
        return self.time
    
    def get_username(self):
        return self.username
