import json 
import os 
from address_allocator import * 
from fonctions_configuration import *
from drap_n_drop_bot import * 

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

    # Ouvrir et lire le fichier JSON, charger les données
    with open('14routers.json', 'r') as file:
        data = json.load(file)

    # Extraire les informations AS du JSON, créer des instances de la classe AS, les stocker dans la liste all_as
    all_as = [AS(as_info['number'], as_info['IP_range'], as_info['loopback_range'], as_info['protocol'], as_info['routers']) 
            for as_info in data['AS']]

    all_as_dict = generate_as_dict(all_as)
            
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
        drag_file(i, fichiers_config)
        
