import json

def create_gns3_project_file():
    # Structure de base d'un fichier .gns3 (projet GNS3)
    with open('gns3.json', 'r') as file:
        gns3_project_data = json.load(file)
    # Ouvrir et écrire dans le fichier 'projet.gns3'
    with open('projet.gns3', 'w') as file:
        json.dump(gns3_project_data, file, indent=4)  # Écrire les données avec un formatage
    print("Fichier 'projet.gns3' créé avec succès.")