# Embedded file name: ParserGrafcet.pyc
import tpg

class MonErreur(Exception):

    def __init__(self, valeur):
        self.Valeur = valeur

    def __str__(self):
        return self.Valeur


class ObjetNomme():

    def __str__(self):
        """Retourne le nom de l'objet"""
        return self.Nom

    def __rep__(self):
        """Retourne le nom de l'objet"""
        return self.Nom


class Grafcet():

    def __init__(self, nomAppli):
        """  Objet de type Grafcet """
        self.NomAppli = nomAppli
        self.Entrees = []
        self.Sorties = []
        self.Graphes = []
        self.ObjetNomme = {}

    def Afficher(self):
        """Affiche le grafcet"""
        texte = 'Inputs :\n'
        for elt in self.Entrees:
            texte += '- ' + elt.Afficher() + '\n'

        texte += '\nOutputs :\n'
        for elt in self.Sorties:
            texte += '- ' + elt.Afficher() + '\n'

        texte += '\nCharts :\n'
        for elt in self.Graphes:
            texte += elt.Afficher() + '\n'

        print(texte)

    def AjouterEntree(self, nom, commentaire):
        """Ajoute une entree au grafcet"""
        if nom in list(self.ObjetNomme.keys()):
            raise MonErreur('Grafcet declaration: Element "' + nom + '" defined two times...')
        Obj = Entree(nom, commentaire)
        self.ObjetNomme[nom] = Obj
        self.Entrees.append(Obj)

    def AjouterSortie(self, nom, commentaire):
        """Ajoute une sortie au grafcet"""
        if nom in list(self.ObjetNomme.keys()):
            raise MonErreur('Grafcet declaration: Element "' + nom + '" defined two times...')
        Obj = Sortie(nom, commentaire)
        self.ObjetNomme[nom] = Obj
        self.Sorties.append(Obj)

    def AjouterGraphe(self, nature, nom, com, donnees_etapes, donnees_transitions, donnees_actions):
        """Ajoute un graphe"""
        for graphe in self.Graphes:
            if graphe.Nom == nom:
                raise MonErreur('Grafcet declaration: Element "' + nom + '" defined two times...')

        if nature == 'partiel':
            graphe = Graphe(nature, nom, com)
            self.Graphes.append(graphe)
        elif nature == 'expansion':
            if nom not in list(self.ObjetNomme.keys()):
                raise MonErreur('Grafcet declaration: The macro-step "' + nom + '" ' + 'is not defined...')
            objet = self.ObjetNomme[nom]
            if not isinstance(objet, Etape):
                raise MonErreur('Grafcet declaration: The macro-step "' + nom + '" ' + 'is not defined as a step...')
            if objet.Nature != 'macroEtape':
                raise MonErreur('Grafcet declaration: The macro-step "' + nom + '" ' + 'is not defined as a macro-step...')
            graphe = Graphe(nature, nom, com)
            graphe.Macro = objet
            self.Graphes.append(graphe)
            objet.Expansion = graphe
        else:
            raise MonErreur('Not yet defined  : The chart "' + nom + '" can not be stored...')
        for donnee in donnees_etapes:
            nature, nom, initiale, commentaire = donnee
            self.AjouterEtape(nature, nom, initiale, commentaire, graphe)

        for donnee in donnees_transitions:
            nom, amonts, avals, recep, commentaire = donnee
            self.AjouterTransition(nom, amonts, avals, recep, commentaire, graphe)

        for donnee in donnees_actions:
            nature, nom, nomEtape, nomSortie, condition, commentaire = donnee
            self.AjouterAction(nature, nom, nomEtape, nomSortie, condition, commentaire, graphe)

    def AjouterEtape(self, nature, nom, initiale, commentaire, graphe):
        """Ajoute une etape"""
        if nom in list(self.ObjetNomme.keys()):
            raise MonErreur('Grafcet declaration: Element "' + nom + '" defined two times...')
        Obj = Etape(nature, nom, initiale, commentaire, graphe)
        self.ObjetNomme[nom] = Obj
        graphe.Etapes.append(Obj)
        if nature == 'normale':
            pass
        elif nature == 'macroEtape':
            if nom[0] != 'M':
                raise MonErreur('Grafcet declaration: The macro-step "' + nom + '" ' + 'is not correctly defined...')
        elif nature == 'etapeEntree':
            if nom[0] != 'E':
                raise MonErreur('Grafcet declaration: The entry step "' + nom + '" ' + 'is not correctly defined...')
            else:
                graphe.EtapeEntree = Obj
        elif nature == 'etapeSortie':
            if nom[0] != 'S':
                raise MonErreur('Grafcet declaration: The exit step "' + nom + '" ' + 'is not correctly defined...')
            else:
                graphe.EtapeSortie = Obj
        else:
            raise MonErreur('Not yet defined  : The step "' + nom + '" can not be stored...')

    def AjouterTransition(self, nom, amonts, avals, recep, commentaire, graphe):
        """Ajoute une transition"""
        if nom in list(self.ObjetNomme.keys()):
            raise MonErreur('Grafcet declaration: Element "' + nom + '" defined two times...')
        for nomEtape in amonts + avals:
            if nomEtape not in list(self.ObjetNomme.keys()):
                raise MonErreur('Grafcet declaration: Transition "' + nom + ' : step "' + nomEtape + '" not yet defined...')
            if self.ObjetNomme[nomEtape] not in graphe.Etapes:
                raise MonErreur('Grafcet declaration: Transition "' + nom + ' : step "' + nomEtape + '" not defined in the chart...')

        etapesEnAmont = []
        for nomEtape in amonts:
            etapesEnAmont.append(self.ObjetNomme[nomEtape])

        etapesEnAval = []
        for nomEtape in avals:
            etapesEnAval.append(self.ObjetNomme[nomEtape])

        Obj = Transition(nom, etapesEnAmont, etapesEnAval, recep, commentaire)
        self.ObjetNomme[nom] = Obj
        graphe.Transitions.append(Obj)

    def AjouterAction(self, nature, nom, nomEtape, nomSortie, condition, commentaire, graphe):
        """Ajoute une action"""
        if nom in list(self.ObjetNomme.keys()):
            raise MonErreur('Grafcet declaration: Element "' + nom + '" defined two times...')
        if nomEtape not in list(self.ObjetNomme.keys()):
            raise MonErreur('Grafcet declaration Action "' + nom + '" : step "' + nomEtape + '" not yet defined...')
        if self.ObjetNomme[nomEtape] not in graphe.Etapes:
            raise MonErreur('Grafcet declaration: Action "' + nom + '" : step "' + nomEtape + '" not defined in the chart...')
        objEtape = self.ObjetNomme[nomEtape]
        if objEtape.Nature == 'macroEtape':
            raise MonErreur('Grafcet declaration: Action "' + nom + '" : step "' + nomEtape + '" is defined as a macro-step...')
        if nomSortie not in list(self.ObjetNomme.keys()):
            raise MonErreur('Grafcet declaration: Action "' + nom + '" : output "' + nomSortie + '" is not defined...')
        if self.ObjetNomme[nomSortie] not in self.Sorties:
            raise MonErreur('Grafcet declaration: Action "' + nom + '" : "' + nomSortie + '" is not defined as an output...')
        objSortie = self.ObjetNomme[nomSortie]
        if objSortie.Nature == '':
            if nature == 'Assignation' or nature == 'AssignationConditionnelle':
                objSortie.Nature = 'Assignation'
            else:
                objSortie.Nature = 'Affectation'
        elif objSortie.Nature == 'Assignation':
            if nature == 'Set' or nature == 'Reset':
                raise MonErreur('Grafcet declaration: The output "' + nomSortie + '" is simultaneously concerned by stored and continuous action...')
        elif objSortie.Nature == 'Affectation':
            if nature == 'Assignation' or nature == 'AssignationConditionnelle':
                raise MonErreur('Grafcet declaration: The output "' + nomSortie + '" is simultaneously concerned by stored and continuous action...')
        Obj = Action(nature, nom, objEtape, objSortie, condition, commentaire)
        self.ObjetNomme[nom] = Obj
        graphe.Actions.append(Obj)

    def DecoderArbreExpression(self, noeud):
        nature, donnee = noeud
        if nature == 'Var':
            nom = donnee
            nomEtape = donnee[1:]
            if nom in list(self.ObjetNomme.keys()):
                obj = self.ObjetNomme[nom]
                if isinstance(obj, Entree):
                    return Expression('Entree', self.ObjetNomme[nom])
            elif nomEtape in list(self.ObjetNomme.keys()):
                obj = self.ObjetNomme[nomEtape]
                if isinstance(obj, Etape):
                    if obj.Nature == 'macroEtape':
                        raise MonErreur('Not yet defined ' + 'no macro-step can be tested in a transition-condition...')
                    else:
                        return Expression('Etape', self.ObjetNomme[nomEtape])
            else:
                raise MonErreur('Grafcet declaration: Element "' + nom + '" not defined...')
        elif nature == 'NON':
            return Expression(nature, self.DecoderArbreExpression(donnee))
        if nature == 'Cte':
            return Expression(nature, donnee)
        if nature == 'ET' or nature == 'OU':
            liste = []
            for data in donnee:
                elt = self.DecoderArbreExpression(data)
                liste.append(elt)

            return Expression(nature, liste)
        raise MonErreur('Not yet defined ' + 'This operator ' + '"' + nature + '" can not be used in this version...')


class Etape(ObjetNomme):

    def __init__(self, nature, nom, initiale, commentaire, graphe):
        """ Etape du grafcet : nature,nom,initiale(Boolean),commentaire """
        self.Nature = nature
        self.Nom = nom
        self.Initiale = initiale
        self.Commentaire = commentaire
        self.Pere = graphe
        self.TransitionsEnAmont = []
        self.TransitionsEnAval = []
        self.Actions = []
        self.Active = False
        self.ActiveAvant = False
        self.AActiver = False
        self.ADesactiver = False

    def Afficher(self):
        """Retourne une cha\xeene de caract\xe8res contenant les infos sur l'\xe9tape"""
        chaine = self.Nom
        if self.Nature == 'macroEtape':
            chaine += ' : Macro-step'
        elif self.Nature == 'etapeEntree':
            chaine += ' : Input step'
        elif self.Nature == 'etapeSortie':
            chaine += ' : Output step'
        if self.Initiale:
            chaine += ' : Initial'
        if self.Commentaire != '':
            chaine += ' ' + self.Commentaire
        return chaine + ' ;'

    def ValideTransition(self):
        """Retourne True si l'\xe9tape ou la macro-\xe9tape valide la transition"""
        if self.Nature == 'macroEtape':
            return self.Expansion.EtapeSortie.Active
        else:
            return self.Active

    def A_Activer(self):
        if self.Nature == 'macroEtape':
            self.Expansion.EtapeEntree.AActiver = True
        else:
            self.AActiver = True

    def A_Desactiver(self):
        if self.Nature == 'macroEtape':
            self.Expansion.EtapeSortie.ADesactiver = True
        else:
            self.ADesactiver = True

    def CalculerActive(self):
        """Calcule si l'etape est active"""
        self.ActiveAvant = self.Active
        self.Active = self.AActiver or self.Active and not self.ADesactiver
        self.AActiver = False
        self.ADesactiver = False


class Transition(ObjetNomme):

    def __init__(self, nom, etapesEnAmont, etapesEnAval, recep, commentaire):
        self.Nom = nom
        self.EtapesEnAmont = etapesEnAmont
        self.EtapesEnAval = etapesEnAval
        self.Commentaire = commentaire
        self.ReceptiviteArbre = recep
        self.Validee = False
        self.Franchissable = False
        for etape in self.EtapesEnAmont:
            if etape.Nature == 'etapeSortie':
                raise MonErreur('Grafcet declaration: Transition "' + nom + ' : step "' + etape.Nom + '" is a exit step...')
            else:
                etape.TransitionsEnAval.append(self)

        for etape in self.EtapesEnAval:
            if etape.Nature == 'etapeEntree':
                raise MonErreur('Grafcet declaration: Transition "' + nom + ' : step "' + etape.Nom + '" is a entry step...')
            else:
                etape.TransitionsEnAmont.append(self)

    def Afficher(self):
        """Retourne une cha\xeene de caract\xe8res contenant les infos sur l'\xe9tape"""
        chaine = '    - ' + self.Nom
        amont = ''
        for etape in self.EtapesEnAmont:
            amont += etape.Nom + ', '

        aval = ''
        for etape in self.EtapesEnAval:
            aval += etape.Nom + ', '

        chaine += ' : ' + amont[:-2] + ' : ' + aval[:-2] + ' : ' + self.Receptivite.Afficher()
        if self.Commentaire != '':
            chaine += ' ' + self.Commentaire
        return chaine + ' ;'

    def CalculerValidee(self):
        """Calcule si la transition est validee"""
        self.Franchissable = False
        self.Validee = True
        for etape in self.EtapesEnAmont:
            if not etape.ValideTransition():
                self.Validee = False

    def Franchir(self):
        """D\xe9sactive les \xe9tapes amont et active les \xe9tapes aval"""
        for etape in self.EtapesEnAmont:
            etape.A_Desactiver()

        for etape in self.EtapesEnAval:
            etape.A_Activer()


class Action(ObjetNomme):

    def __init__(self, nature, nom, objEtape, objSortie, condition, commentaire):
        self.Nom = nom
        self.EtapeAssociee = objEtape
        self.SortieAssociee = objSortie
        self.Commentaire = commentaire
        self.EtapeAssociee.Actions.append(self)
        self.SortieAssociee.Actions.append(self)
        if nature == 'Set' or nature == 'Reset':
            self.Nature = 'Affectation'
            self.Operation = nature
            if condition == 'Activation' or condition == 'Desactivation':
                self.Instant = condition
            else:
                self.Instant = 'Condition'
                self.ConditionArbre = condition
        else:
            self.Nature = nature
            self.ConditionArbre = condition

    def Afficher(self):
        """Retourne une cha\xeene de caract\xe8res contenant les infos sur l'action"""
        chaine = self.Nom + ' : '
        if self.Nature == 'Assignation':
            chaine += 'Continuous : ' + self.EtapeAssociee.Nom + ' : ' + self.SortieAssociee.Nom
        elif self.Nature == 'AssignationConditionnelle':
            chaine += 'Continuous : ' + self.EtapeAssociee.Nom + ' : ' + self.SortieAssociee.Nom
            chaine += ' : ' + self.Condition.Afficher()
        elif self.Nature == 'Affectation':
            chaine += self.Operation + ' : ' + self.EtapeAssociee.Nom + ' : ' + self.SortieAssociee.Nom + ' : '
            if self.Instant == 'Activation' or self.Instant == 'Desactivation':
                chaine += self.Instant
            else:
                chaine += ' : ' + self.Condition.Afficher()
        if self.Commentaire != '':
            chaine += ' ' + self.Commentaire
        return chaine + ' ;'


class Graphe(ObjetNomme):

    def __init__(self, nature, nom, commentaire):
        """  Objet de type Graphe : nom, commentaire """
        self.Nature = nature
        self.Nom = nom
        self.Commentaire = commentaire
        self.Etapes = []
        self.Transitions = []
        self.Actions = []
        self.Tempos = []

    def Afficher(self):
        """Retourne une cha\xeene de caract\xe8res contenant les infos sur le graphe"""
        chaine = '\n- ' + self.Nom
        if self.Commentaire != '':
            chaine += ' ' + self.Commentaire
        chaine += '\n  - Steps:\n'
        for elt in self.Etapes:
            chaine += '    - ' + elt.Afficher() + '\n'

        chaine += '  - Transitions:\n'
        for elt in self.Transitions:
            chaine += elt.Afficher() + '\n'

        chaine += '  - Actions:\n'
        for elt in self.Actions:
            chaine += '    - ' + elt.Afficher() + '\n'

        return chaine


class Entree(ObjetNomme):

    def __init__(self, nom, commentaire):
        """ Entree du mod\xe8le : nom, commentaire """
        self.Nom = nom
        self.Commentaire = commentaire
        self.Valeur = False
        self.ValeurAvant = False

    def Afficher(self):
        """Retourne une cha\xeene de caract\xe8res contenant les infos"""
        chaine = self.Nom
        if self.Commentaire != '':
            chaine += ' ' + self.Commentaire
        return chaine + ' ;'


class Sortie(Entree):

    def __init__(self, nom, commentaire):
        """ Sortie du mod\xe8le : nom, commentaire """
        Entree.__init__(self, nom, commentaire)
        self.Actions = []
        self.Nature = ''


class Expression():

    def __init__(self, nature, donnee, duree = ''):
        self.Nature = nature
        self.Donnee = donnee
        if nature == 'TON' or nature == 'TOF':
            self.Duree = duree

    def Afficher(self):
        """Retourne une cha\xeene de caract\xe8res contenant l'expression"""
        if self.Nature == 'Entree':
            return self.Donnee.Nom
        if self.Nature == 'Etape':
            return 'X' + self.Donnee.Nom
        if self.Nature == 'ET':
            chaine = ''
            for operande in self.Donnee:
                if operande.Nature == 'OU':
                    chaine += '.(' + operande.Afficher() + ')'
                else:
                    chaine += '.' + operande.Afficher()

            return chaine[1:]
        if self.Nature == 'OU':
            chaine = ''
            for operande in self.Donnee:
                chaine += '+' + operande.Afficher()

            return chaine[1:]
        if self.Nature == 'Cte':
            if self.Donnee == 'Vrai':
                return '=1'
            else:
                return '=0'
        else:
            if self.Donnee.Nature == 'Entree' or self.Donnee.Nature == 'Etape':
                chaine = self.Donnee.Afficher()
            else:
                chaine = '(' + self.Donnee.Afficher() + ')'
            if self.Nature == 'NON':
                return '/' + chaine
            if self.Nature == 'FM':
                return '>' + chaine
            if self.Nature == 'FD':
                return '<' + chaine
            if self.Nature == 'TON':
                return self.Duree + '/' + chaine
            if self.Nature == 'TOF':
                return chaine + '/' + self.Duree
            return '???'


class Info():

    def __init__(self, prenom = '', nom = '', comAuteur = '', date = '', commentaire = ''):
        self.Prenom = prenom
        self.Nom = nom
        self.ComAuteur = comAuteur
        self.Date = date
        self.Commentaire = commentaire

    def Afficher(self):
        if self.Nom != '':
            chaine = 'Author : ' + self.Prenom + ' ' + self.Nom + ' ' + self.ComAuteur + '\n'
            if self.Date != '':
                chaine += 'Date : ' + self.Date + '\n'
            if self.Commentaire != '':
                chaine += self.Commentaire + '\n'
            return chaine
        else:
            return ''


class DescriptionTextuelle(tpg.Parser):
    r"""
    separator spaces : '\s+' ;
    separator comments : '#.*' ;
    token Commentaire : '\(\*.*\*\)' ;
    token Date : '\d\d\/\d\d\/\d\d' ;
    token par_ouv : '\(' ;
    token par_fer : '\)' ;
    token Egal : '=' ;
    token Duree : '\d+(s|ms|mn)' ;
    token Var : '\w(\w|\-)*' ;
    
    #
    # Grafcet
    #
    START/<Inf,Ent,Sor,Gra> -> $Inf=''$ (Infos/Inf)? '<GRAFCET>' Entrees/Ent Sorties/Sor Graphes/Gra '</GRAFCET>' ;
    #
    # Infos
    #
    Infos/<auteur,date,com> -> $date='';com=''$ '<INFO>' Auteur/auteur ('Date' ':' Date/date)? (Commentaire/com)? '</INFO>' ;
    Auteur/<prenom,nom,com> -> $com=''$ 'Author' ':' Var/prenom Var/nom (Commentaire/com)? ;
    #
    # Entrees
    #
    Entrees/Ent -> $Ent=[]$ '<INPUTS>' (Entree/e $Ent.append(e)$ )*  '</INPUTS>' ;
    Entree/<nom,com> -> $com=''$ Var/nom (Commentaire/com)? ';' ;
    #
    # Sorties
    #
    Sorties/Sor -> $Sor=[]$ '<OUTPUTS>' (Sortie/s $Sor.append(s)$ )*  '</OUTPUTS>' ;
    Sortie/<nom,com> -> $com=''$ Var/nom (Commentaire/com)? ';' ;
    #
    # Graphes
    #
    Graphes/Gra -> $Gra=[]$ '<CHARTS>' ((Partiel/p | Expansion/p) $Gra.append(p)$ )*  '</CHARTS>' ;
    Partiel/<'partiel',nom,com,Eta,Tra,Act> -> $com='';Tra=[];Act=[]$ '<PARTIAL' 'Name' '=' Var/nom '>' (Commentaire/com)?
        Etapes/Eta (Transitions/Tra)? (Actions/Act)? '</PARTIAL>' ;
    Expansion/<'expansion',nom,com,Eta,Tra,Act> -> $com='';Tra=[];Act=[]$ '<EXPANSION' 'Name' '=' Var/nom '>' (Commentaire/com)?
        EtapesExpansion/Eta (Transitions/Tra)? (Actions/Act)? '</EXPANSION>' ;
    #
    # Etapes
    #
    Etapes/Eta -> $Eta=[]$ '<STEPS>' ( (Etape/e | MacroEtape/e) $Eta.append(e)$ )*  '</STEPS>' ;
    Etape/<nature,nom,init,com> -> $nature='normale';com='';init=False$ Var/nom (Initialisation/init)? (Commentaire/com)? ';' ;
    Initialisation/$True$ -> ':' 'Initial' ;
    EtapesExpansion/Eta -> $Eta=[]$ '<STEPS>' EtapeEntree/e $Eta.append(e)$
        ((Etape/e | MacroEtape/e) $Eta.append(e)$ )* EtapeSortie/e $Eta.append(e)$  '</STEPS>' ;
    MacroEtape/<nature,nom,init,com> -> $nature='macroEtape';com='';init=False$ Var/nom ':' 'Macro\-step' (Commentaire/com)? ';' ;
    EtapeEntree/<nature,nom,init,com> -> $nature='etapeEntree';com='';init=False$ Var/nom ':' 'Entry' 'step' (Initialisation/init)? (Commentaire/com)? ';' ;
    EtapeSortie/<nature,nom,init,com> -> $nature='etapeSortie';com='';init=False$ Var/nom ':' 'Exit' 'step' (Initialisation/init)? (Commentaire/com)? ';' ;
    #
    # Transitions
    #
    Transitions/Tra -> $Tra=[]$ '<TRANSITIONS>' (Transition/t $Tra.append(t)$ )*  '</TRANSITIONS>' ;
    Transition/$(nom,amonts,avals,rec,com)$ -> $com=''$ Var/nom ':' EnsEtapes/amonts ':'EnsEtapes/avals ':'Expression/rec (Commentaire/com)? ';' ;
    EnsEtapes/Ens -> $Ens=[]$ (Var/et $Ens.append(et)$ (',' Var/et $Ens.append(et)$ )* )?  ;
    #
    # Actions
    #
    Actions/Act ->  $Act=[]$ '<ACTIONS>' ( ( Assignation/a | Affectation/a ) $Act.append(a)$ )*  '</ACTIONS>' ;
    Assignation/<nature,nom,etape,sortie,cond,com> -> $nature='Assignation';com='';cond=''$
        Var/nom ':' 'Continuous' ':' Var/etape ':' Var/sortie
        (':' Expression/cond $nature='AssignationConditionnelle'$)? (Commentaire/com)? ';' ;
    Affectation/<nature,nom,etape,sortie,cond,com> -> $com=''$
        Var/nom ':' 'Stored' ':' Var/etape ':' Var/sortie ':' ('Set'/nature | 'Reset'/nature) ':'
        ( 'Activation'/cond | 'Desactivation'/cond | Expression/cond ) (Commentaire/com)? ';' ;
    #
    # Expression
    #
    Expression/exp -> ( ExpNnaire/exp | ExpUnaire/exp | Atome/exp | Vrai/exp | Faux/exp ) ;
    ExpNnaire/exp -> ( Somme/exp | Produit/exp ) ;
    ExpUnaire/exp -> ( Negation/exp | FrontMontant/exp | FrontDescendant/exp | TON/exp | TOF/exp) ;    
    Atome/exp -> ( Litteral/exp |  ( par_ouv ( ExpNnaire/exp | ExpUnaire/exp ) par_fer ) ) ;    
    Litteral/<'Var',d> -> Var/d ;
    Vrai/<'Cte',True> -> '=1'/d ;
    Faux/<'Cte',False> -> '=0'/d ;
    Negation/<'NON',d> -> '\/' (Atome/d | ExpUnaire/d ) ;
    FrontMontant/<'FM',d> -> '>' Litteral/d ;
    FrontDescendant/<'FD',d> -> '<' Litteral/d ;
    TON/<'TON',donnee> -> Duree/duree '\/' Atome/sig $donnee=(sig,duree)$;
    TOF/<'TOF',donnee> -> Atome/sig '\/' Duree/duree ;
    Produit/<'ET',l> -> $l=[]$ TermeProduit/t $l.append(t)$ ('\.' TermeProduit/t $l.append(t)$ )+ ;
    Somme/<'OU',l> -> $l=[]$ TermeSomme/t $l.append(t)$ ('\+' TermeSomme/t $l.append(t)$ )+ ;
    TermeProduit/t -> (Atome/t | ExpUnaire/t ) ;
    TermeSomme/t -> ( Produit/t | Atome/t | ExpUnaire/t ) ;
        
    """
    pass


Decoder = DescriptionTextuelle()

def ImporterGrafcet(nomAppli):
    """Cr\xe9e l'objet grafcet correspondant au texte. """
    print('Grafcet import from file', nomAppli + '.txt')
    try:
        fichier = open(nomAppli + '.txt', 'r')
        lignes = fichier.readlines()
        fichier.close()
        texte = ''
        for ligne in lignes:
            texte += ligne

        donneesInfo, donneesEntrees, donneesSorties, donneesGraphes = Decoder(texte)
        if donneesInfo != '':
            auteur, date, commentaire = donneesInfo
            prenom, nom, comAuteur = auteur
            Grafcet.Info = Info(prenom, nom, comAuteur, date, commentaire)
        else:
            Grafcet.Info = Info()
        grafcet = Grafcet(nomAppli)
        for donnee in donneesEntrees:
            nom, commentaire = donnee
            grafcet.AjouterEntree(nom, commentaire)

        for donnee in donneesSorties:
            nom, commentaire = donnee
            grafcet.AjouterSortie(nom, commentaire)

        for donnee in donneesGraphes:
            nature, nom, com, etapes, transitions, actions = donnee
            grafcet.AjouterGraphe(nature, nom, com, etapes, transitions, actions)

        for graphe in grafcet.Graphes:
            for transition in graphe.Transitions:
                transition.Receptivite = grafcet.DecoderArbreExpression(transition.ReceptiviteArbre)

            for action in graphe.Actions:
                if action.Nature == 'AssignationConditionnelle':
                    action.Condition = grafcet.DecoderArbreExpression(action.ConditionArbre)
                elif action.Nature == 'Affectation':
                    if action.Instant == 'Condition':
                        action.Condition = grafcet.DecoderArbreExpression(action.ConditionArbre)

    except IOError as erreur:
        print('- Impossible to access to file')
        print('  -', erreur, '\n')
    except tpg.Error as erreur:
        print('- Syntax error detected by TPG:')
        print(' -', erreur, '\n')
    except MonErreur as erreur:
        print('- Semantic error detected in Grafcet description:')
        print('  -', erreur, '\n')
    else:
        print('- Grafcet successfully imported.\n')
        return (grafcet, texte)