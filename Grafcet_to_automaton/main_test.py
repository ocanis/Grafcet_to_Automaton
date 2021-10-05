#from ParserGrafcet import ImporterGrafcet, DescriptionTextuelle, Grafcet, Info
from ParserGrafcet import *
import tpg
from tpg import Parser

def get_grafcetExamples_path():
	import os
	import sys
	from pathlib import Path
	eg_path = os.path.dirname(os.path.realpath(sys.argv[0])) + "\\Examples\\"
	return eg_path

## Input your txt grafcet
eg_grafcet = "aSimpleGrafcet1"
eg_grafcet_path = get_grafcetExamples_path() + eg_grafcet
print("Grafcet Examples path : ", eg_grafcet_path)

## Let's load grafcet e.g.
from ParserGrafcet import *

Decoder = DescriptionTextuelle()

myGrafcet = Grafcet(eg_grafcet_path)
myGrafcet1 = ImporterGrafcet(eg_grafcet_path)
myGrafcet2 = Grafcet(myGrafcet1)

print("Loaded Grafcet : \n",myGrafcet2)

print(myGrafcet1)
myGrafcet2.Afficher()
# #myGrafcet2.AjouterEtape(m)
# myGrafcet2.AjouterEtape(nature="normale", nom='10', initiale=True, commentaire="None", graphe=myGrafcet2)
# myGrafcet2.Afficher()


from Grafcet_to_Automaton import *

#print(setattr(myGrafcet2, 'ConsoliderDonnees', ConsoliderDonnees))
myGrafcet2.GenererBDD()