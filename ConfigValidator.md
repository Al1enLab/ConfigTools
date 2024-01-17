# ConfigValidator
Classe python `ConfigValidator`.

## Validation et typage pour `configparser.ConfigParser`
`ConfigValidator` étend la classe native python `configparser.ConfigParser` pour lui apporter la validation d'une configuration :
- par la vérification de la présence de variables requises
- par la vérification du typage de ces variables

## Propriétés ajoutées à `configparser.ConfigParser`
- `configdef` : dictionnaire définissant le contenu et les variables de la configuration

## Méthodes ajoutées à `configparser.ConfigParser`
- `validate()` : Vérifie la validité de la configuration en fonction de configdef
- `to_dict()` : exporte la configuration sous la forme d'un dictionnaire python
- `to_typed_dict()` : exporte la configuration sous la forme d'un dictionnaire python avec des valeurs typées
- `to_object()` : exporte la configuration sous la forme d'un objet dont les propriétés sont les variables
- `to_typed_object()` : exporte la configuration sous la forme d'un objet dont les propriétés sont les variables typées

## Structure de `configdef`
```python
definition = {
    '<nom de la section>': {
        'required': True|False                  # section requise ou optionnelle,
        'content': {                            # contenu de la section
            '<nom de variable>': {
                'required': True|False,         # variable requise ou optionnelle
                'type': [ <type1>, <type2> ],   # types de la variable (liste ou type unique)
                'allowed': [ 'val1', 'val2' ]   # valeurs autorisées pour cette variable
            },
            '<nom de variable 2>': {
                'type': int
            },
            '<nom de variable 3>': {
                'allowed': ['yes', 'no' ]
            },
        }
    },
    '<nom de la section 2>': {
        'required': False,
        'content': {
            'var1': { 'required': True, 'type': int, 'allowed': [ 1, 2 ] }
        }
    }
}
```

## Utilisation de la classe `ConfigValidator`
`ConfigValidator` s'utilise comme `configparser.ConfigParser`, avec un paramètre positionnel obligatoire supplémentaire : `configdef`, à savoir la définition de la configuration, détaillée ci-dessus.
Exemple :
```python
definition = {
    'Section1': {
        'required': True,
        'content': {
            'MyVar1': {
                'required': True,
                'type': int
            }
        }
    }
}
conf = ConfigValidator(definition)
conf.read('config.ini')
conf.validate()
```
