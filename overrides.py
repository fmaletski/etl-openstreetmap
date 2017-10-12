"""
Collection of overrides dictionaries created during the data cleaning process
For more information on why and how they were created, see Project.ipynb
"""

streetOverrides = {
    'rua Samanbaia -179- São Francisco -Araucária': 'Rua Samambaia',
    'RUA VICENTE DE CARVALHO': 'Rua Vicente de Carvalho',
    'Filipinas': 'Rua Filipinas',
    'Comendador Franco': 'Avenida Comendador Franco',
    'BR-116': 'Rodovia Régis Bittencourt',
    'Rui Barbosa': 'Praça Rui Barbosa',
    'Vicente za': 'Rua Carlos Vicente Zapxon',
    'domingos benatto': 'Rua Júlio Perneta',
    'Residencial Simão Brante': 'Rua Simão Brante',
}

specialStreetOverrides = {
    'Centro Politécnico da UFPR, Caixa Postal 19100':[
        {
            'id': 3794309563,
            'key': 'name',
            'value': 'Centro Politécnico da UFPR, Caixa Postal 19100',
            'type': 'regular'
        },
        {
            'id': 3794309563,
            'key': 'street',
            'value': 'Avenida Coronel Francisco H. dos Santos',
            'type': 'addr'
        }
    ]
}