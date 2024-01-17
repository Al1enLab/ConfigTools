from types import SimpleNamespace
import configparser

class ConfigValidator(configparser.ConfigParser):

    def __init__(self, configdef, *args, **kwargs):
        '''
        configdef: dictionnaire définissant la configuration
        '''
        self.configdef = configdef
        super().__init__(*args, **kwargs)
    
    def validate(self, strict=False):
        '''
        Validation de la configuration
        strict :    si strict est True, une exception est levée si une variable
                    de la configuration n'est pas expressément déclarée dans la
                    définition de la configuration
        '''
        # On vérifie que les sections requises sont présentes dans la configuration...
        for section, sectiondef in self.configdef.items():
            if section in self:
                # ... et si elle y est et que du contenu est défini, on vérifie les variables...
                if 'content' in sectiondef:
                    for var, vardef in sectiondef['content'].items():
                        if var in self[section]:
                            # On commence par type notre valeur
                            value = self.typevar(section, var)
                            # Si la définition comporte une liste de valeurs autorisées, on vérifie
                            if 'allowed' in vardef and value not in vardef['allowed']:
                                raise ValueError(f'Value \'{self[section][var]}\' not allowed for variable {var} in section [{section}]')
                        elif 'required' in vardef and vardef['required']:
                            raise KeyError(f'Required variable {var} in section [{section}] not found in config file')
            # ... sinon, si elle est requise, on raise
            elif sectiondef['required']:
                raise KeyError(f'Required section [{section}] not found in config file')
        
        # Si le mode strict est activé, on vérifie qu'il n'y a pas de section et de variables en dehors de la définition de la configuration
        if strict:
            # On commence par voir s'il n'y a pas de section indéfinie...
            for section in self.sections():
                if section in self.configdef:
                    # ... et on en fait de même pour les variables
                    for var in self[section]:
                        if 'content' not in self.configdef[section] or var not in self.configdef[section]['content']:
                            raise KeyError(f'Unknown variable {var} in section [{section}] - strict mode')        
                else:
                    raise KeyError(f'Unknown section [{section}] - strict mode')
        return True

    def typevar(self, section, var):
        '''
        Retourne la valeur de la variable var de la section section typée
        conformément à la définition de la configuration.
        Si aucun type n'est sépcifié, retourne la valeur telle quelle.
        Si la valeur ne peut pas être convertie dans le type, raise.
        '''
        value = self[section][var]
        # On commence par vérifier si des types sont définis...
        try:
            vartypes = self.configdef[section]['content'][var]['type']
        except KeyError:
            vartypes = None
        if vartypes is not None:
            # ... et si c'est le cas
            try:
                _ = iter(vartypes)
            except TypeError:
                vartypes = [ vartypes ]
            # ... on essaie d'appliquer chaque type à la valeur de la variable
            for vartype in vartypes:
                try:
                    return vartype(value)
                except ValueError:
                    pass
            raise ValueError(f'Section [{section}]: could not convert \'{var}\' to {" / ".join([ t.__name__ for t in vartypes ])}')
        return value
    
    def to_dict(self):
        '''
        Retourne la configuration au format dict
        Toutes les valeurs sont des chaînes de caractères
        '''
        return { section: dict(self.items(section)) for section in self.sections() }
    
    def to_typed_dict(self):
        '''
        Retourne la configuration au format dict
        Si la définition de la configuration mentionne le type, les variables
        sont typées accordément - ou raise si la conversion est impossible
        '''
        configdict = self.to_dict()
        for section, content in configdict.items():
            for var in content:
                content[var] = self.typevar(section, var)
        return configdict

    def to_object(self):
        '''
        Retourne la configuration sous la forme d'un SimpleNamespace
        '''
        output = SimpleNamespace()
        for section in self.sections():
            setattr(output, section, SimpleNamespace(**dict(self.items(section))))
        return output

    def to_typed_object(self):
        '''
        Retourne la configuration au format SimpleNamespace
        avec les variables typées conformément à la définition de la configuration
        '''
        output = SimpleNamespace()
        for section in self.sections():
            setattr(output, section, SimpleNamespace())
            for var, value in self.items(section):
                setattr(getattr(output, section), var, self.typevar(section, var))
        return output