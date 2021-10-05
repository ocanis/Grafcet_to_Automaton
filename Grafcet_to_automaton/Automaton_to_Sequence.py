# Embedded file name: Automaton_to_Sequence.pyc
import time
import copy
from Grafcet_to_Automaton import *

def GenererMachineMealy(self):
    """ """
    print('\nGeneration of the Mealy machine')
    dateDebut = time.time()
    listePoids = []
    listeRang = []
    self.AlphabetSortie = set([])
    ad = 0
    for objet in self.GrafcetPere.Entrees:
        objet.Poids = ad
        listePoids.append(ad)
        listeRang.append(objet.Rang)
        ad += 1

    ad = 0
    for objet in self.GrafcetPere.Sorties:
        objet.Poids = ad
        ad += 1

    nbEntree = len(self.GrafcetPere.Entrees)
    listeEntree = list(range(nbEntree))
    for codeBinaire in GenererCodeBinaire(nbEntree):
        codeEntree = 0
        minterme = []
        for n in listeEntree:
            if codeBinaire[nbEntree - n - 1]:
                codeEntree += 2 ** listePoids[n]
                minterme.append(listeRang[n])

        for loc in self.LocalitesStables:
            if loc.CondStabilite.AbsorbeMinterme(minterme):
                loc.MealyEntrees.append(codeEntree)
            else:
                for evol in loc.EvolEnAval:
                    if evol.Condition.AbsorbeMinterme(minterme):
                        evol.MealyEntrees.append(codeEntree)
                        break

    for localite in self.LocalitesStables:
        codeSortie = 0
        for sortie in localite.Sorties:
            codeSortie += 2 ** sortie.Poids

        localite.MealySortie = codeSortie
        self.AlphabetSortie.add(codeSortie)

    dateFin = time.time()
    self.DureeGenerationMealy = int((dateFin - dateDebut) * 1000)
    NbreEtat = len(self.LocalitesStables)
    NbreTrans = NbreEtat * 2 ** nbEntree
    print('-', NbreEtat, 'states,', NbreTrans, 'transitions.')
    print('- Duration :', AfficherDuree(self.DureeGenerationMealy))


setattr(GrapheLocalites, 'GenererMachineMealy', GenererMachineMealy)

def ExporterMachineMealy(self, nomAppli, texteGrafcet):
    """ Export de la machine de Mealy dans un fichier texte """
    longMax = 5000
    nom_fichier = nomAppli + '_mealy.txt'
    fichier = open(nom_fichier, 'w')
    fichier.writelines(texteGrafcet)
    nbEtats = len(self.LocalitesStables)
    nbEntrees = 2 ** len(self.GrafcetPere.Entrees)
    nbSorties = len(self.AlphabetSortie)
    nbTransitions = nbEtats * nbEntrees
    texte = '\n\n<MEALY MACHINE>\n\n'
    texte += '#' * 70 + '\n#\n# Constitution of the Mealy machine:\n'
    texte += '# - Number of states: ' + str(nbEtats) + '\n'
    texte += '# - Number of transitions : ' + str(nbTransitions) + '\n'
    texte += '# - Size of the Inputs alphabet: ' + str(nbEntrees) + '\n'
    texte += '# - Size of the Outputs alphabet: ' + str(nbSorties) + '\n'
    texte += '# - Duration of generation : ' + AfficherDuree(self.DureeGenerationMealy) + '\n'
    texte += '#\n' + '#' * 70 + '\n'
    texte += '\n<TRANSITIONS>\n# Source : Target : Input code,Output code'
    texte += '\n#\n# Input code: I0 = ' + self.GrafcetPere.Entrees[0].Nom
    texte += '\n# - 0 : /I3./I2./I1./I0\n# - 1 : /I3./I2./I1.I0\n# - 2 : /I3./I2.I1./I0'
    texte += '\n#\n# Output code: O0 = ' + self.GrafcetPere.Sorties[0].Nom
    texte += '\n# - 0 : /O3./O2./O1./O0\n# - 1 : /O3./O2./O1.O0\n# - 2 : /O3./O2.O1./O0\n'
    longTexte = len(texte)
    for loc in self.LocalitesStables:
        nomSource = loc.AfficherNum()
        nomDestination = loc.AfficherNum()
        nomSortie = str(loc.MealySortie)
        ajout = '\n# From state ' + nomSource + '\n'
        for entree in loc.MealyEntrees:
            ajout += nomSource + ' : ' + nomDestination + ' : ' + repr(entree) + ',' + nomSortie + '\n'

        texte += ajout
        longTexte += len(ajout)
        if longTexte > longMax:
            fichier.writelines(texte)
            texte = ''
            longTexte = 0
        for evol in loc.EvolEnAval:
            ajout = ''
            locAval = evol.Destination
            nomDestination = locAval.AfficherNum()
            nomSortie = str(locAval.MealySortie)
            for entree in evol.MealyEntrees:
                ajout += nomSource + ' : ' + nomDestination + ' : ' + repr(entree) + ',' + nomSortie + '\n'

            texte += ajout
            longTexte += len(ajout)
            if longTexte > longMax:
                fichier.writelines(texte)
                texte = ''
                longTexte = 0

    texte += '\n</TRANSITIONS>\n\n</MEALY MACHINE>\n'
    fichier.writelines(texte)
    fichier.close()
    print('- Results written in file', nom_fichier)


setattr(GrapheLocalites, 'ExporterMachineMealy', ExporterMachineMealy)

def ReduireMachineMealy(self):
    """Elimine les selfloops qui ne doivent pas faire l'objet d'un test specifique"""
    nbBoucleAutoTestee = 0
    for loc in self.LocalitesStables:
        tmp = loc.MealyEntrees[:]
        for entree in tmp:
            for evol in loc.EvolEnAmont:
                if entree in evol.MealyEntrees:
                    loc.MealyEntrees.remove(entree)
                    nbBoucleAutoTestee += 1
                    break

    print("\nAnalysis of the Mealy machine\n- Number of selfloops which don't need a specific test:", nbBoucleAutoTestee)


setattr(GrapheLocalites, 'ReduireMachineMealy', ReduireMachineMealy)

def GenererSequenceTest(self, nomAppli):
    """ Generation de la structure du graphe pour le Chinese Postman Problem """
    print('\nGeneration of the test sequence')
    dateDebut = time.time()
    listLoc = []
    for loc in self.LocalitesStables:
        listLoc.append(loc.Num)

    GrapheCPP = CPP(listLoc, 1)
    for loc in self.LocalitesStables:
        nomSource = loc.Num
        nomDestination = loc.Num
        sortie = loc.MealySortie
        for entree in loc.MealyEntrees:
            GrapheCPP.addArc((entree, sortie), nomSource, nomDestination)

        for evol in loc.EvolEnAval:
            locAval = evol.Destination
            nomDestination = locAval.Num
            sortie = locAval.MealySortie
            for entree in evol.MealyEntrees:
                GrapheCPP.addArc((entree, sortie), nomSource, nomDestination)

    GrapheCPP.solve_R()
    GrapheCPP.calcCPT_R()
    dateFin = time.time()
    self.DureeGenerationSequence = int((dateFin - dateDebut) * 1000)
    print('- Size of the test sequence : ' + str(len(GrapheCPP.CPT)))
    print('- Duration :', AfficherDuree(self.DureeGenerationSequence))
    GrapheCPP.ExporterCPT(nomAppli, self.GrafcetPere)


setattr(GrapheLocalites, 'GenererSequenceTest', GenererSequenceTest)

class CPP:

    def __init__(self, vertices, startVertex):
        """Cree la structure d'accueil du Chinese Postman Problem"""
        self.vertices = vertices
        self.startVertex = startVertex
        self.delta = {}
        self.neg = []
        self.pos = []
        self.arcs = {}
        self.label = {}
        self.c = {}
        self.f = {}
        self.cheapestLabel = {}
        self.defined = {}
        self.path = {}
        self.CPT = []
        for i in vertices:
            self.delta[i] = 0
            self.arcs[i] = {}
            self.label[i] = {}
            self.c[i] = {}
            self.f[i] = {}
            self.cheapestLabel[i] = {}
            self.defined[i] = {}
            self.path[i] = {}
            for j in vertices:
                self.arcs[i][j] = 0
                self.label[i][j] = []
                self.c[i][j] = 0
                self.f[i][j] = 0
                self.cheapestLabel[i][j] = ''
                self.defined[i][j] = False
                self.path[i][j] = None

        return

    def addArc(self, lab, u, v, cost = 1):
        """Ajoute un arc et renseigne la base de donn\xe9es"""
        self.label[u][v].append(lab)
        self.arcs[u][v] += 1
        self.delta[u] += 1
        self.delta[v] -= 1
        if not self.defined[u][v] or self.c[u][v] > cost:
            self.c[u][v] = cost
            self.cheapestLabel[u][v] = lab
            self.defined[u][v] = True
            self.path[u][v] = v

    def findPath(self, origine, f):
        for i in self.vertices:
            if f[origine][i] > 0:
                return i

        return None

    def leastCostPaths(self):
        for k in self.vertices:
            for i in self.vertices:
                if self.defined[i][k]:
                    for j in self.vertices:
                        if self.defined[k][j] and (not self.defined[i][j] or self.c[i][j] > self.c[i][k] + self.c[k][j]):
                            self.path[i][j] = self.path[i][k]
                            self.c[i][j] = self.c[i][k] + self.c[k][j]
                            self.defined[i][j] = True
                            if i == j and self.c[i][j] < 0:
                                return

    def improvements(self):
        residual = CPP(self.vertices, self.startVertex)
        for i in self.neg:
            for j in self.pos:
                residual.addArc('', i, j, self.c[i][j])
                if self.f[i][j] != 0:
                    residual.addArc('', j, i, -self.c[i][j])

        residual.leastCostPaths()
        for i in self.vertices:
            if residual.c[i][i] < 0:
                k = 0
                kunset = True
                u = i
                loop = True
                while loop:
                    v = residual.path[u][i]
                    if residual.c[u][v] < 0 and (kunset or k > self.f[v][u]):
                        k = self.f[v][u]
                        kunset = False
                    u = v
                    if u == i:
                        loop = False

                u = i
                loop = True
                while loop:
                    v = residual.path[u][i]
                    if residual.c[u][v] < 0:
                        self.f[v][u] -= k
                    else:
                        self.f[u][v] += k
                    u = v
                    if u == i:
                        loop = False

                return True

        return False

    def solve_R(self):
        self.leastCostPaths()
        for i in self.vertices:
            for j in self.vertices:
                if not self.defined[i][j]:
                    raise Error('Graph is not strongly connected')

            if self.c[i][i] < 0:
                raise Error('Graph has a negative cycle')

        for i in self.vertices:
            if self.delta[i] < 0:
                self.neg.append(i)
            elif self.delta[i] > 0:
                self.pos.append(i)

        delta = copy.deepcopy(self.delta)
        for i in self.neg:
            for j in self.pos:
                if -delta[i] < delta[j]:
                    self.f[i][j] = -delta[i]
                else:
                    self.f[i][j] = delta[j]
                delta[i] += self.f[i][j]
                delta[j] -= self.f[i][j]

        while self.improvements():
            pass

    def calcCPT_R(self):
        arcs = copy.deepcopy(self.arcs)
        f = copy.deepcopy(self.f)
        v = self.startVertex
        while True:
            u = v
            v = self.findPath(u, f)
            if v != None:
                f[u][v] -= 1
                while u != v:
                    p = self.path[u][v]
                    self.CPT.append((u, p, self.cheapestLabel[u][p]))
                    u = p

            else:
                bridgeVertex = self.path[u][self.startVertex]
                if arcs[u][bridgeVertex] == 0:
                    break
                v = bridgeVertex
                for i in self.vertices:
                    if i != bridgeVertex and arcs[u][i] > 0:
                        v = i
                        break

                arcs[u][v] -= 1
                self.CPT.append((u, v, self.label[u][v][arcs[u][v]]))

        return

    def ExporterCPT(self, nomAppli, grafcet):
        """ Export de la sequence CPT dans un fichier texte """
        longMax = 5000
        nom_fichier = nomAppli + '_sequence.txt'
        fichier = open(nom_fichier, 'w')
        texte = '#' * 70 + '\n#\n#Structure of the test sequence :\n'
        texte += '# - Size of the test sequence: ' + str(len(self.CPT)) + '\n'
        texte += '# - Duration of generation : ' + AfficherDuree(grafcet.GLA.DureeGenerationSequence) + '\n'
        texte += '#\n' + '#' * 70 + '\n\n'
        texte += '\n<TEST>\n\n<ENTREES>\n'
        for elt in grafcet.Entrees:
            texte += '  ' + elt.Afficher() + '\n'

        texte += '</ENTREES>\n\n<SORTIES>\n'
        for elt in grafcet.Sorties:
            texte += '  ' + elt.Afficher() + '\n'

        texte += '</SORTIES>\n\n'
        texte += '<SEQUENCE>\n'
        texte += '\n<TRANSITIONS>\n# Step : Source : Target : Input code : Output code ;'
        texte += '\n#\n# Input code: I0 = ' + grafcet.Entrees[0].Nom
        texte += '\n# - 0 : /I3./I2./I1./I0\n# - 1 : /I3./I2./I1.I0\n# - 2 : /I3./I2.I1./I0'
        texte += '\n#\n# Output code: O0 = ' + grafcet.Sorties[0].Nom
        texte += '\n# - 0 : /O3./O2./O1./O0\n# - 1 : /O3./O2./O1.O0\n# - 2 : /O3./O2.O1./O0\n'
        longTexte = len(texte)
        pas = 0
        for elt in self.CPT:
            pas += 1
            source, destination, label = elt
            entree, sortie = label
            ajout = repr(pas) + ' : ' + repr(source) + ' : ' + repr(destination) + ' : ' + repr(entree) + ' : ' + repr(sortie) + ' ;\n'
            texte += ajout
            longTexte += len(ajout)
            if longTexte > longMax:
                fichier.writelines(texte)
                texte = ''
                longTexte = 0

        texte += '</SEQUENCE>\n\n</TEST>\n'
        fichier.writelines(texte)
        fichier.close()
        print('- Results written in file', nom_fichier)