import requests
import json

url = "http://127.0.0.1:8000"

"""class PoliceStation(models.Model):
    pid = models.BigAutoField(primary_key=True)
    # district in which police station is located
    did = models.ForeignKey(District,to_field="did",db_column="district_did",on_delete=models.CASCADE)
    # Name of the police station
    name = models.TextField()
    # address of the police station
    address = models.TextField(null=True)
    # GPS location of the police station
    lat = models.DecimalField(max_digits=9,decimal_places=6,default=0.0)
    long = models.DecimalField(max_digits=9,decimal_places=6, default=0.0)"""
 

class TestDistrictClass:    

    def __init__(self):
        self.url = url

    def get(self, id):
        print("\nDisplaying district for id :",id)
        url = f"{self.url}/police-station-get/{id}"
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
        print("\n Adding Police station ")
        data = {
            "did":"7005698992", 
            "name":"name of first police station", 
            "address":"address of first police station", 
            "lat":"53.2734", 
            "long":"-7.77832031"
            }
        json_data  = json.dumps(data)
        print("\n Adding Police station",json_data)
        url = f"{self.url}/district-create/"
        r = requests.post(url = url, json=json_data)
        
        for x in r:
            print (x)
    
    def update(self, id):
            print("\n Updating District")
            data = {'name':'Lowe Subansiri'}
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

def testDistrict():
    t = TestDistrictClass()
    t.list()
    #t.get(6)
    #t.add()
    #t.update(5)
    #t.delete(4)

if __name__ == '__main__':
    testDistrict()
 

