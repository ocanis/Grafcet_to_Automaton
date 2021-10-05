# Embedded file name: Grafcet_to_Automaton.pyc
import tpg
import time
from ParserGrafcet import *
from robdd import *

def GenererBDD(self):
    """Retourne le BDD correspondant \xe0 l'expression"""
    if self.Nature == 'Entree' or self.Nature == 'Etape':
        return self.Donnee.Exp
    if self.Nature == 'Cte':
        if self.Donnee:
            return BDD.Vrai
        else:
            return BDD.Faux
    else:
        if self.Nature == 'ET':
            bdd = BDD.Vrai
            for operande in self.Donnee:
                bdd &= operande.GenererBDD()

            return bdd
        if self.Nature == 'OU':
            bdd = BDD.Faux
            for operande in self.Donnee:
                bdd |= operande.GenererBDD()

            return bdd
        if self.Nature == 'NON':
            return ~self.Donnee.GenererBDD()
        ch = 'Case not yet defined:\n The expression"' + self.Afficher() + '"  can not be coded with a BDD...'
        raise MonErreur(ch)


setattr(Expression, 'GenererBDD', GenererBDD)

def EliminerVariablesEtat(self, listeAUn, premiereEntree):
    """Retourne le sous-bdd"""
    if self.Terminal:
        return self
    if self.Ord < premiereEntree:
        if self.Ord in listeAUn:
            return self.Hi.EliminerVariablesEtat(listeAUn, premiereEntree)
        else:
            return self.Lo.EliminerVariablesEtat(listeAUn, premiereEntree)
    else:
        return self


setattr(BDD, 'EliminerVariablesEtat', EliminerVariablesEtat)

def AbsorbeMinterme(self, minterme):
    """ Retourne True si self est vrai lorque minterme est vrai """
    if self.Terminal:
        return self.TjsVrai
    elif self.Ord in minterme:
        return self.Hi.AbsorbeMinterme(minterme)
    else:
        return self.Lo.AbsorbeMinterme(minterme)


setattr(BDD, 'AbsorbeMinterme', AbsorbeMinterme)

def ConsoliderDonnees(self):
    """Cree les donnees ROBDD correspondantes"""
    InitialiserStructure()
    for graphe in self.Graphes:
        for etape in graphe.Etapes:
            etape.Exp = CreerLitteral(etape.Nom)
            etape.Rang = etape.Exp.Ord

    for graphe in self.Graphes:
        for tempo in graphe.Tempos:
            tempo.Exp = CreerLitteral(tempo.Nom)
            tempo.Rang = tempo.Exp.Ord

    for entree in self.Entrees:
        entree.Exp = CreerLitteral(entree.Nom)
        entree.Rang = entree.Exp.Ord

    for graphe in self.Graphes:
        for transition in graphe.Transitions:
            transition.Exp = transition.Receptivite.GenererBDD()

    for sortie in self.Sorties:
        if sortie.Nature == 'Assignation':
            sortie.Exp = BDD.Faux
            for action in sortie.Actions:
                if action.Nature == 'AssignationConditionnelle':
                    sortie.Exp |= action.EtapeAssociee.Exp & action.Condition.GenererBDD()
                else:
                    sortie.Exp |= action.EtapeAssociee.Exp


setattr(Grafcet, 'ConsoliderDonnees', ConsoliderDonnees)

def GenererGrapheLocalites(self, affichage):
    """Construit le graphe des localites correspondant au grafcet"""
    print('Generation of the stable location automaton')
    dateDebut = time.time()
    gla = GrapheLocalites(self)
    self.CondAcces = BDD.Vrai
    for graphe in self.Graphes:
        for etape in graphe.Etapes:
            etape.Active = etape.Initiale

    gla.LocInit.ReleverLocalite()
    gla.GenererArbreEvolution(gla.LocInit, True, affichage)
    while len(gla.LocalitesStablesInexplorees) > 0:
        loc = gla.LocalitesStablesInexplorees.pop(0)
        gla.GenererArbreEvolution(loc, False, affichage)
        gla.LocalitesStables.append(loc)

    for n in range(len(gla.LocalitesStables)):
        gla.LocalitesStables[n].Num = n + 1

    NbreLoc = str(len(gla.LocalitesStables) + 1)
    NbreEvol = str(len(gla.Evolutions))
    NbreInst = str(len(gla.InstabilitesTotales))
    dateFin = time.time()
    print('-', NbreLoc, 'locations,', NbreEvol, 'evolutions,', NbreInst, 'totally unstable evolutions')
    gla.DureeGenerationGla = int((dateFin - dateDebut) * 1000)
    print('- Duration :', AfficherDuree(gla.DureeGenerationGla))
    return gla


setattr(Grafcet, 'GenererGrapheLocalites', GenererGrapheLocalites)

class GrapheLocalites():

    def __init__(self, grafcet):
        """Cree la structure d'accueil du graphe des localites"""
        self.GrafcetPere = grafcet
        grafcet.GLA = self
        self.LocalitesStablesInexplorees = []
        self.LocalitesStables = []
        self.LocalitesInexplorees = []
        self.LocalitesAtteintes = []
        self.InstabilitesTotales = []
        self.Evolutions = []
        self.LocInit = Localite(grafcet)

    def ExporterGla(self, nomAppli, texteGrafcet):
        """ Export  des resultats dans un fichier texte """
        longMax = 5000
        nom_fichier = nomAppli + '_automaton.txt'
        fichier = open(nom_fichier, 'w')
        fichier.writelines(texteGrafcet)
        texte = '\n\n<EQUIVALENT AUTOMATON>\n\n'
        texte += '#' * 70 + '\n#\n# Constitution of the stable location automaton :\n'
        texte += '# - Number of locations: ' + str(len(self.LocalitesStables) + 1) + '\n'
        texte += '# - Number of evolutions: ' + str(len(self.Evolutions)) + '\n'
        texte += '# - Number of totally unstable evolutions: ' + str(len(self.InstabilitesTotales)) + '\n#\n'
        texte += '# - Duration of generation : ' + AfficherDuree(self.DureeGenerationGla) + '\n'
        texte += '#\n' + '#' * 70 + '\n'
        texte += '\n<LOCATIONS>\n'
        texte += '  0 : INIT ;\n'
        longTexte = len(texte)
        for elt in self.LocalitesStables:
            ajout = '  ' + elt.AfficherNum() + ' : ' + elt.Afficher() + ' ;\n'
            texte += ajout
            longTexte += len(ajout)
            if longTexte > longMax:
                fichier.writelines(texte)
                texte = ''
                longTexte = 0

        texte += '</LOCATIONS>\n\n'
        texte += '<EVOLUTIONS>\n'
        for elt in self.Evolutions:
            ajout = '  ' + elt.Afficher() + ' ;\n'
            texte += ajout
            longTexte += len(ajout)
            if longTexte > longMax:
                fichier.writelines(texte)
                texte = ''
                longTexte = 0

        texte += '</EVOLUTIONS>\n\n'
        if self.InstabilitesTotales != []:
            texte += '<UNSTABLE EVOLUTIONS>\n'
            for elt in self.InstabilitesTotales:
                ajout = '  ' + elt.Afficher() + ' ;\n'
                texte += ajout
                longTexte += len(ajout)
                if longTexte > longMax:
                    fichier.writelines(texte)
                    texte = ''
                    longTexte = 0

            texte += '</UNSTABLE EVOLUTIONS>\n\n'
        texte += '</EQUIVALENT AUTOMATON>\n'
        fichier.writelines(texte)
        fichier.close()
        print('- Results written in file', nom_fichier)

    def GenererArbreEvolution(self, localite, initialisation = False, affichage = False):
        """"""
        localite.IssueDe = None
        localite.CondAcces = BDD.Vrai
        localite.FixerLocalite()
        expNonFranch, transFranch = localite.ReleverTransitionsFranchissables(BDD.Vrai)
        expNonChang, sortiesPossibles = localite.ReleverVariationSorties(expNonFranch)
        if initialisation:
            if not expNonChang.EstZero():
                localite.EnregistrerLocaliteStable(expNonChang, initialisation, affichage)
        else:
            localite.CondStabilite = expNonChang
        ensTransFranch = localite.CalculerEnsemblesSimultanes(transFranch)
        for elt in ensTransFranch:
            localite.EnregistrerLocaliteAtteinteFranchissement(elt, localite, affichage)

        ensSortiesPossibles = localite.CalculerEnsemblesSimultanes(sortiesPossibles)
        for elt in ensSortiesPossibles:
            localite.EnregistrerLocaliteAtteinteVariation(elt, localite, affichage)

        while len(self.LocalitesInexplorees) > 0:
            loc = self.LocalitesInexplorees.pop(0)
            self.LocalitesAtteintes.append(loc)
            if affichage:
                print('-', loc.Afficher())
            loc.FixerLocalite()
            expNonFranch, transFranch = loc.ReleverTransitionsFranchissables(loc.CondAcces)
            expNonChang, sortiesPossibles = loc.ReleverVariationSorties(expNonFranch)
            if not expNonChang.EstZero():
                loc.EnregistrerLocaliteStable(expNonChang, False, affichage)
            ensTransFranch = loc.CalculerEnsemblesSimultanes(transFranch)
            for elt in ensTransFranch:
                loc.EnregistrerLocaliteAtteinteFranchissement(elt, localite, affichage)

            ensSortiesPossibles = loc.CalculerEnsemblesSimultanes(sortiesPossibles)
            for elt in ensSortiesPossibles:
                loc.EnregistrerLocaliteAtteinteVariation(elt, localite, affichage)

        return


class Localite():
    """"""

    def __init__(self, grafcet, issueDe = None):
        """Cree un objet localite"""
        self.GrafcetPere = grafcet
        self.Num = 0
        self.Etapes = []
        self.Sorties = []
        self.TempoActives = []
        self.TempoEcoulees = []
        self.TempoLancees = []
        self.TempoArretees = []
        self.Stable = False
        self.IssueDe = issueDe
        self.DueA = set([])
        self.Nom = ''
        self.CondAcces = BDD.Vrai
        self.CondStabilite = None
        self.EvolEnAmont = []
        self.EvolEnAval = []
        self.MealyEntrees = []
        self.MealyEntreesATester = []
        return

    def Afficher(self):
        chaine = '('
        ch = ''
        for elt in self.Etapes:
            ch += elt.Nom + ','

        if ch == '':
            chaine += '{} '
        else:
            chaine += '{' + ch[:-1] + '},'
        ch = ''
        for elt in self.Sorties:
            ch += elt.Nom + ','

        if ch == '':
            chaine += '{}'
        else:
            chaine += '{' + ch[:-1] + '}'
        if self.CondStabilite != None:
            chaine += ',' + self.CondStabilite.Afficher()
        return chaine + ')'

    def AfficherNum(self):
        return repr((self.Num))

    def ReleverLocalite(self):
        """"""
        for graphe in self.GrafcetPere.Graphes:
            for etape in graphe.Etapes:
                if etape.Active:
                    self.Etapes.append(etape)

            for tempo in graphe.Tempos:
                if tempo.Ecoulee:
                    self.TempoEcoulees.append(tempo)
                if tempo.Active:
                    self.TempoActives.append(tempo)
                if tempo.Lancee:
                    self.TempoLancees.append(tempo)
                if tempo.Arretee:
                    self.TempoArretees.append(tempo)

        for sortie in self.GrafcetPere.Sorties:
            if sortie.Valeur:
                self.Sorties.append(sortie)

        self.CondAcces = self.GrafcetPere.CondAcces

    def FixerLocalite(self):
        """Fixe la localite courante dans le grafcet"""
        if self.IssueDe == None:
            amont = self
        else:
            amont = self.IssueDe
        for graphe in self.GrafcetPere.Graphes:
            for etape in graphe.Etapes:
                etape.Active = etape in self.Etapes
                etape.ActiveAvant = etape in amont.Etapes

            for tempo in graphe.Tempos:
                tempo.Ecoulee = tempo in self.TempoEcoulees
                tempo.Active = tempo in self.TempoActives
                tempo.Lancee = tempo in self.TempoLancees
                tempo.Arretee = tempo in self.TempoArretees

        for sortie in self.GrafcetPere.Sorties:
            sortie.Valeur = sortie in self.Sorties

        self.GrafcetPere.CondAcces = self.CondAcces
        self.EliminerVariablesEtat()
        return

    def EliminerVariablesEtat(self):
        """Pour chaque transition et chaque sortie par assignation
        Fait pointer ExpCour sur le sous BDD compatibles avec les variables d'\xe9tats courantes"""
        listeAUn = []
        premiereEntree = self.GrafcetPere.Entrees[0].Rang
        for graphe in self.GrafcetPere.Graphes:
            for etape in graphe.Etapes:
                if etape.Active:
                    listeAUn.append(etape.Rang)

            for tempo in graphe.Tempos:
                if tempo.Ecoulee:
                    listeAUn.append(tempo.Rang)

        for graphe in self.GrafcetPere.Graphes:
            for transition in graphe.Transitions:
                transition.ExpCour = transition.Exp.EliminerVariablesEtat(listeAUn, premiereEntree)

        for sortie in self.GrafcetPere.Sorties:
            if sortie.Nature == 'Assignation':
                sortie.ExpCour = sortie.Exp.EliminerVariablesEtat(listeAUn, premiereEntree)

    def ReleverTransitionsFranchissables(self, condition):
        """Retourne la liste des transitions franchissables depuis la localit\xe9 courante"""
        exp = condition
        transitionsFranchissables = []
        for graphe in self.GrafcetPere.Graphes:
            for transition in graphe.Transitions:
                transition.CalculerValidee()
                if transition.Validee and not transition.ExpCour.ProduitEstZero(condition):
                    exp &= ~transition.ExpCour
                    triplet = (transition, transition.ExpCour & condition, set([]))
                    transitionsFranchissables.append(triplet)

        return (exp, transitionsFranchissables)

    def ReleverVariationSorties(self, condition):
        """Retourne la liste des sorties pouvant varier"""
        exp = condition
        sortiesPossibles = []
        for sortie in self.GrafcetPere.Sorties:
            if sortie.Nature == 'Assignation':
                if sortie in self.Sorties:
                    expSortie = sortie.ExpCour.Complementaire
                else:
                    expSortie = sortie.ExpCour
                if not expSortie.ProduitEstZero(condition):
                    exp &= ~expSortie
                    triplet = (sortie, expSortie & condition, set([]))
                    sortiesPossibles.append(triplet)

        return (exp, sortiesPossibles)

    def CalculerEnsemblesSimultanes(self, listeElements):
        """Liste de triplet : Element, BDD, ensembleVide """
        nbreElements = len(listeElements)
        ensemblesFranchissables = []
        ensemblesTailleN = []
        nouveauxEnsembles = []
        for n1 in range(nbreElements):
            t1 = listeElements[n1][0]
            cond1 = listeElements[n1][1]
            elt = (set([t1]), cond1, n1)
            ensemblesTailleN.append(elt)

        for n1 in range(nbreElements):
            t1 = listeElements[n1][0]
            cond1 = listeElements[n1][1]
            for n2 in range(n1 + 1, nbreElements):
                t2 = listeElements[n2][0]
                cond2 = listeElements[n2][1]
                if not cond1.ProduitEstZero(cond2):
                    listeElements[n1][2].add(t2)
                    listeElements[n2][2].add(t1)
                    cond = cond1 & cond2
                    elt = (set([t1, t2]), cond, n2)
                    nouveauxEnsembles.append(elt)

        while len(ensemblesTailleN) > 0:
            while len(ensemblesTailleN) > 0:
                elt = ensemblesTailleN.pop(0)
                ens = elt[0]
                cond = elt[1]
                for elt1 in nouveauxEnsembles:
                    if elt1[0].issuperset(ens):
                        cond &= ~elt1[1]

                if not cond.EstZero():
                    ensemblesFranchissables.append((ens, cond))

            ensemblesTailleN = nouveauxEnsembles
            nouveauxEnsembles = []
            for elt1 in ensemblesTailleN:
                ens1 = elt1[0]
                cond1 = elt1[1]
                for n in range(elt1[2] + 1, nbreElements):
                    elt2 = listeElements[n]
                    if elt2[2].issuperset(ens1):
                        cond2 = elt2[1]
                        if not cond1.ProduitEstZero(cond2):
                            cond = cond1 & cond2
                            ens = ens1.copy()
                            ens.add(elt2[0])
                            nouveauxEnsembles.append((ens, cond, n))

        return ensemblesFranchissables

    def EnregistrerLocaliteAtteinteFranchissement(self, ensTransitionsFranchissables, localiteDepart, affichage):
        """Enregistre la localit\xe9 atteinte par franchissement d'un ensemble de transitions """
        self.FixerLocalite()
        self.GrafcetPere.CondAcces = ensTransitionsFranchissables[1]
        for transition in ensTransitionsFranchissables[0]:
            transition.Franchir()

        for graphe in self.GrafcetPere.Graphes:
            for etape in graphe.Etapes:
                etape.CalculerActive()

            for tempo in graphe.Tempos:
                pass

        for sortie in self.GrafcetPere.Sorties:
            if sortie.Nature == 'Affectation':
                sortie.AActiver = False
                sortie.ADesactiver = False
                for action in sortie.Actions:
                    etape = action.EtapeAssociee
                    if etape.Active and not etape.ActiveAvant and action.Instant == 'Activation' or not etape.Active and etape.ActiveAvant and action.Instant == 'Desactivation':
                        if action.Operation == 'Set':
                            sortie.AActiver = True
                        else:
                            sortie.ADesactiver = True

                sortie.Valeur = sortie.AActiver or sortie.Valeur and not sortie.ADesactiver

        localite = Localite(self.GrafcetPere, self)
        localite.ReleverLocalite()
        localite.DueA = ensTransitionsFranchissables[0]
        if localite.EstTotalementInstable():
            self.GrafcetPere.GLA.InstabilitesTotales.append(Evolution(localite, True))
        else:
            self.GrafcetPere.GLA.LocalitesInexplorees.append(localite)
        if affichage:
            ch = ''
            for transition in ensTransitionsFranchissables[0]:
                ch += transition.Nom + ' '

            ch += ': ' + localite.Afficher() + ' : ' + ensTransitionsFranchissables[1].Afficher()
            print(ch)

    def EnregistrerLocaliteAtteinteVariation(self, ensSortiesPossibles, localiteDepart, affichage):
        """Enregistre la localit\xe9 atteinte par variation d'un ensemble de sorties """
        self.FixerLocalite()
        self.GrafcetPere.CondAcces = ensSortiesPossibles[1]
        for sortie in ensSortiesPossibles[0]:
            sortie.Valeur = not sortie.Valeur

        localite = Localite(self.GrafcetPere, self)
        localite.ReleverLocalite()
        if affichage:
            ch = ''
            for sortie in ensSortiesPossibles[0]:
                ch += sortie.Nom + ' '

            ch += ': ' + localite.Afficher() + ' : ' + ensSortiesPossibles[1].Afficher()
            print(ch)
        localite.DueA = ensSortiesPossibles[0]
        localite.EnregistrerLocaliteStable(ensSortiesPossibles[1], False, affichage)

    def EnregistrerLocaliteStable(self, condition, initialisation, affichage):
        """"""
        gla = self.GrafcetPere.GLA
        evolution = Evolution(self)
        evolution.Condition = condition
        gla.Evolutions.append(evolution)
        if initialisation:
            localite = Localite(self.GrafcetPere, self)
            localite.Etapes = self.Etapes[:]
            gla.LocalitesStablesInexplorees.append(localite)
            evolution.Source = gla.LocInit
            evolution.Destination = localite
        else:
            stable = None
            for localite in gla.LocalitesStables + gla.LocalitesStablesInexplorees:
                if self.Etapes == localite.Etapes and self.Sorties == localite.Sorties and self.TempoEcoulees == localite.TempoEcoulees:
                    stable = localite
                    break

            if stable == None:
                gla.LocalitesStablesInexplorees.append(self)
            else:
                evolution.Destination = stable
        evolution.Source.EvolEnAval.append(evolution)
        evolution.Destination.EvolEnAmont.append(evolution)
        return

    def EstTotalementInstable(self):
        """"""
        totalementInstable = False
        termine = False
        localite = self.IssueDe
        while localite != None and not totalementInstable:
            if self.Etapes == localite.Etapes and self.Sorties == localite.Sorties and self.TempoEcoulees == localite.TempoEcoulees:
                totalementInstable = True
            localite = localite.IssueDe

        return totalementInstable


class Evolution():

    def __init__(self, destination, instabilite = False):
        self.Condition = destination.CondAcces
        self.Instabilite = instabilite
        if not instabilite:
            self.Destination = destination
        else:
            self.Destination = None
        self.ListeTransitions = []
        localite = destination
        while localite != None:
            source = localite
            self.ListeTransitions.append(localite.DueA)
            localite = localite.IssueDe

        vide = self.ListeTransitions.pop()
        self.Source = source
        self.ListeTransitions.reverse()
        self.MealyEntrees = []
        return

    def Afficher(self):
        chaine = self.Source.AfficherNum() + ' : '
        if not self.Instabilite:
            chaine += self.Destination.AfficherNum() + ' : '
        chaine += self.Condition.Afficher() + ' : '
        ch1 = ''
        for ens in self.ListeTransitions:
            ch2 = ''
            for sortie in self.Source.GrafcetPere.Sorties:
                if sortie in ens:
                    ch2 += sortie.Nom + ','

            for graphe in self.Source.GrafcetPere.Graphes:
                for transition in graphe.Transitions:
                    if transition in ens:
                        ch2 += transition.Nom + ','

            if ch2 == '':
                ch1 += '{} '
            else:
                ch1 += '{' + ch2[:-1] + '},'

        if ch1 == '':
            return chaine + '[{}]'
        else:
            return chaine + '[' + ch1[:-1] + ']'


def GenererCodeBinaire(longueur):
    """ Retourne une liste de 2^longueur codes binaires """
    if longueur == 1:
        return [[False], [True]]
    else:
        liste = GenererCodeBinaire(longueur - 1)
        new_liste = []
        for code in liste:
            copie = code[:]
            code.append(False)
            new_liste.append(code)
            copie.append(True)
            new_liste.append(copie)

        return new_liste


def AfficherDuree(duree):
    """ Retourne une cha\xeene de caract\xe8res repr\xe9sentant 'duree' """
    dureeSeconde = duree / 1000
    ms = duree % 1000
    mn = dureeSeconde / 60
    sec = dureeSeconde % 60
    chaine = ''
    if mn > 0:
        chaine += repr(mn) + ' min ' + repr(sec) + ' s '
    elif sec > 0:
        chaine += repr(sec) + ' s '
    chaine += repr(ms) + ' ms'
    return chaine