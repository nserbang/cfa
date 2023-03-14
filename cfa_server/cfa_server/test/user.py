import requests
import json

url = "http://127.0.0.1:8000"

class testUserClass:
    def __init__(self):
        self.url = url
    def add(self):
        data = {
            'username':'9997698979',
            'first_name':'name_first11',
            'last_name':'name_last',
            'email':'email@gmail.com',
            'password':'password',
            'is_active': True,
            'is_staff': False,
            'is_superuser':False,
            'role':'user',
            'address':'this is addresses',
            'pincode':791110,
            'otp_code':555
        }

        json_data  = json.dumps(data)
        print("\n Creating User",json_data)
        url = f"{self.url}/register/"
        r = requests.post(url = url, json=json_data)
        
        for x in r:
            print (x)
    
    def list(self):        
        url = f"{self.url}/user-list/"
        r = requests.post(url = url)        
        for x in r:
            print (x)
    
    def update(self, pk = None):
        print(" user name ",pk)
        data = {"role":"police",
                "first_name":"Nabam Serbang"}
        json_data  = json.dumps(data)
        print("\n Updating User",json_data)
        url = f"{self.url}/user-update/{pk}"
        
        r = requests.patch(url = url, json=json_data)
        #r = {'d','r'}
        for x in r:
            print (x)
        print(" Url ",url)

def testUser():
    t = testUserClass()
    #t.list()
    #t.get(6)
    #t.add()
    t.update(9997698979)
    #t.delete(4)
     

if __name__ == '__main__':    
    testUser()

