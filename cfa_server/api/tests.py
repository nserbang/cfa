from django.test import TestCase
#from models import *
# Create your tests here.
from models import District

d = District()
d.did = 1233
d.name = "Anini"
d = District()
d.name = "test 1"
print (" Value : ",d)