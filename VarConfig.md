# VarConfig
Classe python `VarConfig`.

## Gestionnaire d'affectation
`VarConfig` permet de configurer simplement les sources de valeurs à affecter à des variables, par exemple lors de l'initialisation d'une classe.

## Concept
Souvent, on doit affecter à une variable une valeur provenant soit des paramètres passés à la fonction, soit d'une variable d'environnement, soit d'un fichier de configuration. Il faut alors vérifier la présence de cette valeur à différents endroits, souvent avec des noms différents.

`VarConfig` se propose de simplifier cette étape avec une configuration à passer en paramètre à son appel.

## Configuration
`VarConfig` permet de déclarer des sources de valeurs dans l'ordre de priorité dans lequel on doit aller les chercher. Par exemple, on peut vouloir affecter à une variable `mavariable` la valeur :
- du paramètre `mavar` passé à la fonction
- si ce paramètre est absent, la valeur de la variable `ma_variable` de la section `ma_section` d'un fichier de configuration
- et en dernier lieu, la valeur de la variable d'environnement `MAVAR`
- enfin, si aucune de ces valeurs n'est présente, alors affecter la valeur `'valeur_defaut'` par défaut

On peut donc définir cette configuration comme suit :
```python
vardef = {
    'mavariable': {
        'source': [
            ( 'localvars', 'mavar'),
            ( 'config', ( 'ma_section', 'ma_variable' ) ),
            ( 'env', 'MAVAR' )
        ],
        'default': 'valeur_defaut'
    }
}
```
On peut ajouter autant de variables qu'on le souhaite à la racine du dictionnaire.

## Utilisation

Supposons une classe qui s'instancie avec les variables suivantes :

| Variable     | Source                      | VariableSource                                   |
|--------------|-----------------------------|--------------------------------------------------|
| `localvar`   | Passée en paramètre         | `mylocalvar`                                     |
| `configvar`  | Fichier de configuration    | Section `MySection`, variable `myconfigvar`      |
| `envvar`     | Environnement               | `MYENVVAR`                                       |
| `multivar`   | 1. Passée en paramètre      | `mylocalmultivar`                                |
|              | 2. Fichier de configuration | Section `MySection`, variable `myconfigmultivar` |
|              | 3. Environnement            | `MYENVMULTIVAR`                                  |
| `defaultvar` | Aucune                      | Défaut : `'MyDefaultValue'`                      | 

### Fichier de configuration

Le fichier de configuration `config.ini` est comme suit :
```
[MySection]
    myconfigvar = MyConfigValue
    myconfigmultivar = MyConfigMultiValue
```

### Déclaration de la configuration

Restranscription du tableau ci-dessus en définition des variables :
```python
vardef = {
    'localvar': {
        'source': [ ( 'localvars', 'mylocalvar' ) ]
    },
    'configvar': {
        'source': [ ( 'config', ( 'MySection', 'myconfigvar' ) ) ]
    },
    'envvar': {
        'source': [ ( 'env', 'MYENVVAR' ) ]
    },
    'multivar' : {
        'source': [
            ( 'localvars', 'mylocalmultivar' ),
            ( 'config', ( 'MySection', 'myconfigmultivar' ) ),
            ( 'env', 'MYENVMULTIVAR' )
        ]
    },
    'defaultvar': {
        'source': [ ( 'localvars', 'nonexisting' ) ],
        'default': 'MyDefaultValue'
    }
}
```

### Déclaration de la classe
```python
from VarConfig import VarConfig
import configparser

class MyClass:

    def __init__(self, localvar, *args, **kwargs):
        # Chargement de la configuration
        fileconfig = configparser.ConfigParser()
        fileconfig.read('config.ini')
        # Affectation des variables via VarConfig
        self.config = VarConfig(vardef, localvars=locals(), config=fileconfig)
```

### Appel à la classe
```python
os.environ['MYENVVAR'] = 'MyEnvValue'
os.environ['MYENVMULTIVAR'] = 'MyEnvMultiValue'

C = MyClass('MyLocalVar')
print(C.config.multivar)
print(C.config.vardict())
```
Et le résultat :
```python
MyConfigMultiValue
{'localvar': 'MyLocalVar', 'configvar': 'MyConfigValue', 'envvar': 'MyEnvValue', 'multivar': 'MyConfigMultiValue', 'defaultvar': 'MyDefaultValue'}
```