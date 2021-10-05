# Embedded file name: robdd.pyc


class BDD():

    def __init__(self, rang, lo, hi, terminal = False, valeur = False):
        """ Un noeud BDD est d\xe9finit par son rang, et ses deux noeuds fils """
        self.Terminal = terminal
        self._Treated = False
        if terminal:
            self.TjsVrai = valeur
            if self.TjsVrai:
                self.Monomes = set([((), ())])
            else:
                self.Monomes = set([])
        else:
            self.Ord = rang
            self.Lo = lo
            self.Hi = hi
            self.Monomes = None
        return

    def __str__(self):
        """ Retourne une cha\xeene de caract\xe8res repr\xe9sentant le BDD """
        if self.Terminal:
            if self.TjsVrai:
                return '1'
            else:
                return '0'
        else:
            nom = BDD.Variables[self.Ord]
            if self.Hi.Terminal:
                simpLo = self.Hi.TjsVrai
                if self.Lo.Terminal:
                    simpHi = self.Lo.TjsVrai
                    chLo = ''
                    if self.Lo.Terminal:
                        if self.Lo.TjsVrai:
                            chLo = '/' + nom
                    elif simpLo:
                        chLo = self.Lo.__str__()
                    else:
                        chLo = '/' + nom + '.' + self.Lo.__str__()
                    chHi = ''
                    if self.Hi.Terminal:
                        chHi = self.Hi.TjsVrai and nom
                elif simpHi:
                    chHi = self.Hi.__str__()
                else:
                    chHi = nom + '.' + self.Hi.__str__()
                return (chLo == '' or chHi == '') and chLo + chHi
            return '(' + chLo + '+' + chHi + ')'

    def __invert__(self):
        """ Retourne le BDD compl\xe9mentaire"""
        return self.Complementaire

    def __rand__(self, other):
        """ Retourne le ET logique entre self et other """
        return self._Appliquer(other, ET=True, OU=False)

    def __ror__(self, other):
        """ Retourne le OU logique entre self et other """
        return self._Appliquer(other, ET=False, OU=True)

    def _CreerNoeudBdd(self, rang, lo, hi):
        """ Retourne le noeud BDD apr\xe8s avoir v\xe9rifi\xe9 si il n'est pas d\xe9j\xe0 construit """
        id_lo = id(lo)
        id_hi = id(hi)
        if id_lo == id_hi:
            noeud = lo
        elif (id_lo, id_hi) in BDD._NoeudsCrees[rang]:
            noeud = BDD._NoeudsCrees[rang][id_lo, id_hi]
        else:
            noeud = BDD(rang, lo, hi)
            BDD._NoeudsCrees[rang][id_lo, id_hi] = noeud
            inverse = BDD(rang, lo.Complementaire, hi.Complementaire)
            BDD._NoeudsCrees[rang][id(lo.Complementaire), id(hi.Complementaire)] = inverse
            noeud.Complementaire = inverse
            inverse.Complementaire = noeud
        return noeud

    def _Appliquer(self, other, ET, OU):
        """ Retourne le r\xe9sultat de l'operation ET ou de l'operation OU sur self et other """
        if self.Terminal or other.Terminal:
            if self.Terminal:
                terminal, quelconque = self, other
            else:
                terminal, quelconque = other, self
            if OU and terminal.TjsVrai or ET and not terminal.TjsVrai:
                return terminal
            else:
                return quelconque
        else:
            id_self = id(self)
            id_other = id(other)
            if id_self < id_other:
                min_id, max_id = id_self, id_other
            else:
                min_id, max_id = id_other, id_self
            if self.Ord == other.Ord:
                if ET:
                    dico = BDD._EtRealises[self.Ord][0]
                elif OU:
                    dico = BDD._OuRealises[self.Ord][0]
                if id_self == id_other:
                    return self
                if self.Complementaire == other:
                    if ET:
                        return BDD.Faux
                    else:
                        return BDD.Vrai
                elif (min_id, max_id) in dico:
                    return dico[min_id, max_id]
                else:
                    lo = self.Lo._Appliquer(other.Lo, ET, OU)
                    hi = self.Hi._Appliquer(other.Hi, ET, OU)
                    noeud = self._CreerNoeudBdd(self.Ord, lo, hi)
                    dico[min_id, max_id] = noeud
                    return noeud

            else:
                if self.Ord < other.Ord:
                    racine, feuille = self, other
                else:
                    racine, feuille = other, self
                if ET:
                    if feuille.Ord not in BDD._EtRealises[racine.Ord][1]:
                        BDD._EtRealises[racine.Ord][1][feuille.Ord] = {}
                    dico = BDD._EtRealises[racine.Ord][1][feuille.Ord]
                elif OU:
                    if feuille.Ord not in BDD._OuRealises[racine.Ord][1]:
                        BDD._OuRealises[racine.Ord][1][feuille.Ord] = {}
                    dico = BDD._OuRealises[racine.Ord][1][feuille.Ord]
                if (min_id, max_id) in dico:
                    return dico[min_id, max_id]
                lo = racine.Lo._Appliquer(feuille, ET, OU)
                hi = racine.Hi._Appliquer(feuille, ET, OU)
                noeud = self._CreerNoeudBdd(racine.Ord, lo, hi)
                dico[min_id, max_id] = noeud
                return noeud

    def EstZero(self):
        """ Retourne True si le BDD est le noeud Zero, False sinon """
        if self.Terminal:
            return not self.TjsVrai
        else:
            return False

    def EstUn(self):
        """ Retourne True si le BDD est le noeud Un, False sinon """
        if self.Terminal:
            return self.TjsVrai
        else:
            return False

    def ProduitEstZero(self, other):
        """ Retourne True si le produit de 'self' et de 'other' peut se ramener a Zero """
        if self.Terminal or other.Terminal:
            if not self.EstZero():
                return other.EstZero()
            elif self.Ord == other.Ord:
                return self == other and False
            else:
                return self.Lo.ProduitEstZero(other.Lo) and self.Hi.ProduitEstZero(other.Hi)
        else:
            if self.Ord < other.Ord:
                racine, feuille = self, other
            else:
                racine, feuille = other, self
            return racine.Lo.ProduitEstZero(feuille) and racine.Hi.ProduitEstZero(feuille)

    def DoubleProduitEstZero(self, one, other):
        """ Retourne True si le produit de 'self' de 'one' et de 'other' peut se ramener a Zero """
        if self.Terminal or one.Terminal or other.Terminal:
            if self.Terminal:
                return not self.TjsVrai or one.ProduitEstZero(other)
            elif one.Terminal:
                return not one.TjsVrai or self.ProduitEstZero(other)
            else:
                return not other.TjsVrai or self.ProduitEstZero(one)
        else:
            liste = [(self.Ord, self), (one.Ord, one), (other.Ord, other)]
            liste.sort()
            rgA, ndA = liste[0]
            rgB, ndB = liste[1]
            rgC, ndC = liste[2]
            if rgA == rgC:
                if ndA.Lo.DoubleProduitEstZero(ndB.Lo, ndC.Lo):
                    return ndA.Hi.DoubleProduitEstZero(ndB.Hi, ndC.Hi)
                return rgA == rgB and ndA.Lo.DoubleProduitEstZero(ndB.Lo, ndC) and ndA.Hi.DoubleProduitEstZero(ndB.Hi, ndC)
            return ndA.Lo.DoubleProduitEstZero(ndB, ndC) and ndA.Hi.DoubleProduitEstZero(ndB, ndC)

    def AbsorbeMonome(self, monome):
        """ Retourne True si self est vrai lorque monome est vrai """
        if self.Terminal:
            return self.TjsVrai
        elif self.Ord in monome[0]:
            return self.Lo.AbsorbeMonome(monome)
        elif self.Ord in monome[1]:
            return self.Hi.AbsorbeMonome(monome)
        else:
            return self.Hi.AbsorbeMonome(monome) and self.Lo.AbsorbeMonome(monome)

    def Afficher(self):
        """ Retourne une chaine de caract\xe8res repr\xe9sentant le BDD en tant somme de produits """
        if self.Terminal:
            if self.TjsVrai:
                return '1'
            else:
                return '0'
        if self.Monomes == None:
            self._RetournerMonomes()
        monomes = []
        for elt in self.Monomes:
            rangs = []
            for rg in elt[0] + elt[1]:
                rangs.append(rg)

            rangs.sort()
            monomes.append((len(elt[0]) + len(elt[1]),
             rangs,
             elt[0],
             elt[1]))

        monomes.sort()
        chaine = ''
        for elt in monomes:
            ch = ''
            for rg in elt[1]:
                if rg in elt[2]:
                    ch += '/'
                ch += BDD.Variables[rg] + '.'

            chaine += ch[:-1] + '+'

        return chaine[:-1]

    def AfficherMiseEnFacteur(self, nom):
        """ Retourne une chaine de caract\xe8res repr\xe9sentant le BDD en montrant l'influence de la variable 'nom'"""
        if nom in BDD.Variables:
            rangVariable = BDD.Variables.index(nom)
        else:
            return self.Afficher()
        if self.Terminal:
            if self.TjsVrai:
                return '1'
            else:
                return '0'
        if self.Monomes == None:
            self._RetournerMonomes()
        monomes = []
        for elt in self.Monomes:
            rangs = []
            for rg in elt[0] + elt[1]:
                rangs.append(rg)

            rangs.sort()
            monomes.append((len(elt[0]) + len(elt[1]),
             rangs,
             elt[0],
             elt[1]))

        monomes.sort()
        chaine = ''
        chaineLo = ''
        chaineHi = ''
        for elt in monomes:
            ch = ''
            for rg in elt[1]:
                if rg == rangVariable:
                    pass
                elif rg in elt[2]:
                    ch += '/' + BDD.Variables[rg] + '.'
                else:
                    ch += BDD.Variables[rg] + '.'

            if rangVariable in elt[2]:
                chaineLo += ch[:-1] + '+'
            elif rangVariable in elt[3]:
                chaineHi += ch[:-1] + '+'
            else:
                chaine += ch[:-1] + '+'

        if chaine.count('+') > 1:
            chaine = '(' + chaine[:-1] + ')+'
        if chaineLo == '+':
            chaine += '/' + nom + '+'
        elif chaineLo != '':
            chaine += '/' + nom + '.(' + chaineLo[:-1] + ')+'
        if chaineHi == '+':
            chaine += nom + '+'
        elif chaineHi != '':
            chaine += nom + '.(' + chaineHi[:-1] + ')+'
        return chaine[:-1]

    def EliminerMonomes(self, expression):
        """Elimine tous les monomes de self si ils satisfont expression """
        if self.Terminal or expression.Terminal:
            pass
        else:
            aEliminer = []
            if self.Monomes == None:
                self._RetournerMonomes()
            for monome in self.Monomes:
                if expression.AbsorbeMonome(monome):
                    aEliminer.append(monome)

            for monome in aEliminer:
                self.Monomes.remove(monome)

        return

    def _RetournerMonomes(self):
        """ Retourne les monomes du noeud BDD"""
        if self.Monomes == None:
            monomesLo = self.Lo._RetournerMonomes()
            monomesHi = self.Hi._RetournerMonomes()
            produit = self.Lo & self.Hi
            monomesProduit = produit._RetournerMonomes()
            self.Monomes = monomesProduit.copy()
            for monome in monomesLo:
                if monome not in monomesProduit:
                    self.Monomes.add(((self.Ord,) + monome[0], monome[1]))

            for monome in monomesHi:
                if monome not in monomesProduit:
                    self.Monomes.add((monome[0], (self.Ord,) + monome[1]))

        return self.Monomes

    def Dimension(self):
        """ Retourne la taille du BDD """
        self._EffacerTrace()
        return self._CompterNoeud()

    def _CompterNoeud(self):
        """ Utilis\xe9 pour retourner la taille du BDD """
        if self._Treated:
            return 0
        else:
            self._Treated = True
            if self.Terminal:
                return 1
            return 1 + self.Lo._CompterNoeud() + self.Hi._CompterNoeud()

    def _EffacerTrace(self):
        """ Positionne \xe0 False la variable Treated dans tout le BDD """
        self._Treated = False
        if not self.Terminal:
            self.Lo._EffacerTrace()
            self.Hi._EffacerTrace()

    def RetournerSousBdd(self, ensemble, rang):
        """ Complete l'ensemble 'ensemble' avec les sous-BDD \xe0 partir du niveau 'rang' """
        if self.Terminal:
            ensemble.add(self)
        elif self.Ord < rang:
            self.Lo.RetournerSousBdd(ensemble, rang)
            self.Hi.RetournerSousBdd(ensemble, rang)
        else:
            ensemble.add(self)


def CreerLitteral(nom):
    """Retourne le BDD correspondant \xe0 la variable"""
    if nom in BDD.Variables:
        return BDD._BddVariables[BDD.Variables.index(nom)]
    else:
        BDD.Variables.append(nom)
        BDD._NoeudsCrees.append({})
        BDD._EtRealises.append(({}, {}))
        BDD._OuRealises.append(({}, {}))
        rang = BDD.Variables.index(nom)
        noeud = BDD.Vrai._CreerNoeudBdd(rang, BDD.Faux, BDD.Vrai)
        BDD._BddVariables.append(noeud)
        noeud.Monomes = set([((), (rang,))])
        noeud.Complementaire.Monomes = set([((rang,), ())])
        return noeud


def InitialiserStructure():
    BDD.Vrai = BDD(None, None, None, True, True)
    BDD.Faux = BDD(None, None, None, True, False)
    BDD.Vrai.Complementaire = BDD.Faux
    BDD.Faux.Complementaire = BDD.Vrai
    BDD.Variables = []
    BDD._BddVariables = []
    BDD._NoeudsCrees = []
    BDD._EtRealises = []
    BDD._OuRealises = []
    return


def AnalyserMemoire():
    """Comptabilise les operations memorisees"""
    nbreNd = 0
    nbreET = 0
    nbreOU = 0
    for var in range(len(BDD.Variables)):
        nbreNd += len(BDD._NoeudsCrees[var])
        nbreET += len(BDD._EtRealises[var][0])
        nbreOU += len(BDD._OuRealises[var][0])
        for var2 in list(BDD._EtRealises[var][1].keys()):
            nbreET += len(BDD._EtRealises[var][1][var2])

        for var2 in list(BDD._OuRealises[var][1].keys()):
            nbreOU += len(BDD._OuRealises[var][1][var2])

    ch = '\nD\xe9tails des op\xe9rations :\n- Noeuds BDD m\xe9moris\xe9s : ' + repr(nbreNd)
    ch += '\n- ET gardes en m\xe9moire : ' + repr(nbreET)
    ch += '\n- OU gardes en m\xe9moire : ' + repr(nbreOU) + '\n'
    print(ch)