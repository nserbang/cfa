import requests
import json

url = "http://127.0.0.1:8000"
class TestDistrictClass:    

    def __init__(self):
        self.url = url
    def get(self, id):
        print("\nDisplaying district for id :",id)
        url = f"{self.url}/district-get/{id}"
        r = requests.get(url)
        for x in r:
            print (x)
      
    def list(self):
        print("\n Listing districts")
        url = f"{self.url}/district-list/"
        r = requests.get(url)
        for x in r:
            print (x)

    def add(self):
        print("\n Adding District")
        data = {'name':'Kra Dadi 2222'}
        json_data  = json.dumps(data)
        print("\n Adding District",json_data)
        url = f"{self.url}/district-create/"
        r = requests.post(url = url, json=json_data)
        
        for x in r:
            print (x)
    
    def update(self, id):
            print("\n Updating District")
            data = {'name':'Pakke Kessang999'}
            json_data  = json.dumps(data)
            print("\n Adding District",json_data)
            url = f"{self.url}/district-update/{id}"
            r = requests.patch(url = url, json=json_data)
        
            for x in r:
                print (x)

    def delete(self, id):
            print("\n Deleting District")
            url = f"{self.url}/district-update/{id}"
            r = requests.delete(url = url)
        
            for x in r:
                print (x)



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

def testDistrict():
    t = TestDistrictClass()
    #t.list()
    #t.get(6)
    t.add()
    #t.update(5)
    #t.delete(4)

def testUser():
    t = testUserClass()
    #t.list()
    #t.get(6)
    t.add()
    #t.update(5)
    #t.delete(4)
     

if __name__ == '__main__':
    #testDistrict()
    testUser()

