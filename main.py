import json 
import os 
import shutil
from address_allocator import * 
from fonctions_configuration import *
from fonctions_config_gns3 import * 


# Définir une fonction pour déplacer un fichier du répertoire source vers le répertoire cible, en écrasant les fichiers portant le même nom dans le répertoire cible
def move_and_overwrite(source_file, target_directory):
    # target_file = os.path.join(target_directory, os.path.basename(source_file))  # Générer le chemin du fichier cible
    # shutil.move(source_file, target_file)  # Déplacer le fichier et écraser le fichier cible

    shutil.move(source_file, target_directory)

def create_folder(name):
    # Vérifier si le dossier 'projet-files' existe déjà
    folder_name = name
    if not os.path.exists(folder_name):
        # Créer le dossier
        os.makedirs(folder_name)
        print(f"Dossier '{folder_name}' créé avec succès.")
    else:
        print(f"Le dossier '{folder_name}' existe déjà.")

if __name__ == "__main__":
    
    # Appeler la fonction pour créer le dossier
    create_folder("resultat/projet-files")
    # os.chdir("resultats")
    # create_folder("dynamips")

    # Ouvrir et lire le fichier JSON, charger les données
    with open('14routers.json', 'r') as file:
        data = json.load(file)

    # Extraire les informations AS du JSON, créer des instances de la classe AS, les stocker dans la liste all_as
    all_as = [AS(as_info['number'], as_info['IP_range'], as_info['loopback_range'], as_info['protocol'], as_info['routers']) 
            for as_info in data['AS']]

    # Créer un dictionnaire as_mapping pour stocker le numéro AS auquel chaque routeur appartient
    as_mapping = {}
    for as_index in all_as:  # Parcourir toutes les instances AS
        for router in as_index.routers:  # Parcourir tous les routeurs dans l'AS
            as_mapping[router.name] = as_index.number  # Mapper le nom du routeur au numéro de l'AS auquel il appartient

    # Créer une liste contenant tous les routeurs
    all_routers = [router for as_index in all_as for router in as_index.routers]

    # Générer le nom de la matrice de connexion à partir de la liste des routeurs et de la carte AS
    connections_matrix_name = generate_connections_matrix_name(all_routers, as_mapping)
    print(connections_matrix_name)  # Imprimer le nom de la matrice de connexion

    # Générer la matrice de connexion à partir de la liste des routeurs et de la carte AS
    connections_matrix = generate_connections_matrix(all_routers, as_mapping)
    print(connections_matrix)  # Imprimer la matrice de connexion

    # Générer un dictionnaire contenant les informations des routeurs
    routers_info = generate_routers_dict(all_as)

    # Initialiser le compteur des types de connexions
    connection_counts = {"111": 0, "112": 0, "border": 0}
    # Parcourir la matrice de connexion pour compter les types de connexions
    for conn in connections_matrix:
        connection_counts[conn[1]] += 1


    # Définir une liste vide pour stocker tous les fichiers source générés
    source_file = []

    # Définir la liste des répertoires cibles : 14 routers
    target_directory = [
        'resultat/project-files/dynamips/5b1ce96a-83fb-42cd-bb74-2f73c9b5e22b/configs/',
        'resultat/project-files/dynamips/2af24f68-e50a-465a-bc73-d92bc75d5bc9/configs/',
        'resultat/project-files/dynamips/8f42c9e7-29d7-4f90-8b65-0a267c3807d8/configs/',
        'resultat/project-files/dynamips/90fa75c6-2d30-460b-bcde-0fd7f687e13d/configs/',
        'resultat/project-files/dynamips/a2b478b3-1c7d-4fe3-b65a-9176ca7b56a2/configs/',
        'resultat/project-files/dynamips/c9e7423a-bef9-41d9-8d79-bd36c13f4135/configs/',
        'resultat/project-files/dynamips/98d4ed54-d28b-47f2-bc68-90fc0728b300/configs/',
        'resultat/project-files/dynamips/3bfb2ca1-93f3-4d67-8bfa-fd81a3a1c953/configs/',
        'resultat/project-files/dynamips/67d4f70d-5a68-463f-9403-cb94b883924b/configs/',
        'resultat/project-files/dynamips/23b5ecaf-8be9-4e5e-86f3-c49fe5fd9533/configs/',
        'resultat/project-files/dynamips/0a0d2352-b2e6-4e0d-a717-1f4728c56f6a/configs/',
        'resultat/project-files/dynamips/7b6d5e47-9238-45d2-bfa5-7463b2300eb4/configs/',
        'resultat/project-files/dynamips/41096a2f-1955-4b16-b574-d0842c1b03a0/configs/',
        'resultat/project-files/dynamips/34b57372-99e1-4ec9-bb80-586af23c24c1/configs/'
    ]

    for folder in target_directory :
        create_folder(folder)

    # Parcourir tous les AS et les routeurs dans chaque AS pour générer les adresses des interfaces pour chaque routeur
    for as_index in all_as:
        for router in as_index.routers:
            generate_interface_addresses(router.name, router.interfaces, connections_matrix, connection_counts)


    fichiers_config = []
    # Parcourir tous les AS et les routeurs dans chaque AS pour générer les fichiers de configuration pour chaque routeur
    for as_index in all_as:
        for router in as_index.routers:
            # Générer l'adresse loopback du routeur
            router_loopback = generate_loopback(router.name, as_index.loopback_range)
            # Générer l'ID du routeur
            router_id = generate_router_id(router.name)
            config = []  # Créer une liste vide pour la configuration
            # Ajouter successivement les configurations de l'en-tête, loopback, interfaces, BGP et de fin
            config.extend(config_head(router.name))
            config.extend(config_loopback(router_loopback, as_index.protocol))
            config.extend(config_interface(router.interfaces, as_index.protocol, router, connections_matrix_name))
            config.extend(config_bgp(router, router_id, all_routers, connections_matrix_name, routers_info))
            config.extend(config_end(as_index.protocol, router_id, router, connections_matrix_name))
            
            # Écrire la configuration dans un fichier
            with open(f"i{router.name[1:]}_startup-config.cfg", 'w') as file:
                file.write('\n'.join(config))  # Écrire le contenu de la configuration
                source_file.append(f"i{router.name[1:]}_startup-config.cfg")  # Ajouter le nom du fichier à la liste source_file
                fichiers_config.append(f"i{router.name[1:]}_startup-config.cfg")
    
    for i in range(len(fichiers_config)):
        move_and_overwrite(fichiers_config[i], target_directory[i])

    # Appeler la fonction pour créer le fichier .gns3
    # create_gns3_project_file()

