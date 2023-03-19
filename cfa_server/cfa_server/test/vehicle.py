import requests
import json

url = "http://127.0.0.1:8000"

class testCaseClass:
    def __init__(self):
        self.url = url
 
    #['caseId','regNumber','chasisNumber','engineNumber','make','model']
    def add(self):
        data = {
            "caseId":"7",
            "regNumber":"Reg1",
            #"chasisNumber":"ChasisNumber",
            "engineNumber":"eno", 
            #"make":"Maruti",    
            "model":"800",           
        }

        json_data  = json.dumps(data)
        print("\n Creating Vehicle ",json_data)
        url = f"{self.url}/lost-vehicle-create/"
        r = requests.post(url = url, json=json_data)
        
        for x in r:
            print (x)
    
    def list(self):        
        url = f"{self.url}/user-list/"
        r = requests.post(url = url)        
        for x in r:
            print (x)
    
    def update(self, pk = None):
        print(" Case Id ",pk)
        data = {"caseId":pk,
                "regNumber":"3333"}                
        json_data  = json.dumps(data)
        print("\n Updating Case",json_data)
        url = f"{self.url}/lost-vehicle-update/{pk}"
        
        r = requests.patch(url = url, json=json_data)
        #r = {'d','r'}
        for x in r:
            print (x)
        print(" Url ",url)

def test():
    t = testCaseClass()
    #t.list()
    #t.get(6)
    #t.add()
    t.update(3)
    #t.delete(4)
     

if __name__ == '__main__':    
    test()

