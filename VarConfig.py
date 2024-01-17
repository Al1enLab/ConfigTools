'''
Classe de gestion de variables de sources multiples
'''
import logging
import os

class VarConfig:

    def __init__(self, vardef, localvars=None, config=None, raise_if_missing=True):
        self.__varconfig_log = logging.getLogger(f'{__name__}.{__class__.__name__}')
        self.__varconfig_log.debug('Initializing')
        self.__vardef = vardef
        self.__localvars = localvars
        self.__config = config
        self.__raise_if_missing = raise_if_missing
        self.__vardict = { }
        self.__assign_vars()
    
    def __assign_vars(self):
        '''
        Renseigne le dictionnaire __vardict avec :
        - en clé, les noms des variables
        - en valeur, les valeurs des ces variables
        '''
        # Pour chaque variable et définition de vairable dans vardef...
        for varname, vardef in self.__vardef.items():
            if 'source' in vardef:
                # ... on prend le nom de la variable à affecter et les sources des valeurs possibles
                for source, sourcename in vardef['source']:
                    # Test des locals
                    if source == 'localvars'and self.__localvars:
                        if sourcename in self.__localvars:
                            self.__vardict[varname] = self.__localvars[sourcename]
                            break
                    # Test des variables d'environnement
                    elif source == 'env' and sourcename in os.environ:
                        self.__vardict[varname] = os.environ.get(sourcename)
                        break
                    # Test du fichier de config
                    elif source == 'config' and self.__config:
                        section, sectionvar = sourcename
                        if section in self.__config.sections():
                            if sectionvar in self.__config[section]:
                                self.__vardict[varname] = self.__config[section][sectionvar]
                                break
                    else:
                        raise ValueError(f'Unknown source {source} for variable {varname}')
            # Si on a trouvé notre variable...
            if varname in self.__vardict:
                # ... on le note en debug
                self.__varconfig_log.debug(f'Variable <{varname}> set from {source}/{sourcename}')
            else:
                # ... sinon on affecte la valeur par défaut si elle existe
                if 'default' in vardef:
                    self.__vardict[varname] = vardef['default']
                    self.__varconfig_log.debug(f'Variable <{varname}> set to default')
                # ... et si elle n'a pas de valeur par défaut, on raise si ce comportement a été choisi
                else:
                    self.__varconfig_log.error(f'Missing variable <{varname}>')
                    if self.__raise_if_missing:
                        raise ValueError(f'Missing variable <{varname}>')

    def vardict(self):
        '''Retourne les variables affectées au format dictionnaire'''
        return self.__vardict
    
    def __getattr__(self, attr):
        '''De quoi accéder aux variables comme propriété de cet objet'''
        if attr in self.__vardict:
            return self.__vardict[attr]
        else:
            raise ValueError(f'Unknown attribute <{attr}>')
