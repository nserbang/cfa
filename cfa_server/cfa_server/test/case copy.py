import requests
import json

url = "http://127.0.0.1:8000"

class testCaseClass:
    def __init__(self):
        self.url = url
 
    
    def add(self):
        data = {
            "pid":"1",
            "user":"7005698992",
            "oid":"1",
            "type":"drug", 
            "title":"My title 2",    
            "cstate":"pending",
            "lat":"34.23", 
            "long":"23.334",    
            "description":"description222", 
            "follow":"False"
        }

        json_data  = json.dumps(data)
        print("\n Creating Case",json_data)
        url = f"{self.url}/case-create/"
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
        data = {"pid":"3",
                "oid":"1",
                "cstate":"resolved",
                "type":"extortion",
                "title": "This is updated title",
                "description":"This is updated description"}
        json_data  = json.dumps(data)
        print("\n Updating Case",json_data)
        url = f"{self.url}/case-update/{pk}"
        
        r = requests.patch(url = url, json=json_data)
        #r = {'d','r'}
        for x in r:
            print (x)
        print(" Url ",url)

def test():
    t = testCaseClass()
    #t.list()
    #t.get(6)
    t.add()
    t.update(9)
    #t.delete(4)
     

if __name__ == '__main__':    
    test()

