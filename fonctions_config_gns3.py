import json
from address_allocator import *

def create_gns3_project_file(AS):
    # Liste des AS avec leurs routeurs et protocoles
    as_data = AS
    
    # Initialisation du contenu du fichier GNS3
    gns3_project_data = {
        "name": "Mon Projet GNS3",
        "version": "2.2.52",
        "type": "topology",
        "topology": {
            "computes": [],
            "drawings": [],
            "links": [],
            "nodes": []
        },
        "auto_open": False,
        "auto_start": False,
        "grid_size": 75,
        "scene_height": 1000,
        "scene_width": 2000,
        "zoom": 100,
        "show_grid": False,
        "snap_to_grid": False,
        "show_layers": False
    }

    # Génération automatique des routeurs et des liens
    node_id_map = {}  # Mapping des noms de routeurs vers leurs IDs
    node_counter = 1
    link_counter = 1

    
    for as_name, as_info in as_data.items():
        protocol = as_info["protocol"]
        routers = as_info["routers"]
        
        # Créer les nœuds pour les routeurs
        for router_name in routers:
            node = {
                "compute_id": "local",
                "name": router_name,
                "node_id": f"node-{node_counter}",
                "node_type": "dynamips",
                "console": 5000 + node_counter,
                "protocol": protocol,
                "properties": {
                    "image": "c7200-advipservicesk9-mz.152-4.S5.image",
                    "platform": "c7200",
                    "ram": 512
                },
                "label": {
                    "text": router_name,
                    "style": "font-family: TypeWriter; font-size: 10.0; font-weight: bold;"
                },
                "x": (node_counter - 1) * 150,  # Positionnement horizontal
                "y": -200 if as_name == "AS111" else 200,  # Positionnement vertical basé sur l'AS
                "width": 66,
                "height": 45
            }
            gns3_project_data["topology"]["nodes"].append(node)
            node_id_map[router_name] = f"node-{node_counter}"
            node_counter += 1
        
        # Créer des liens entre les routeurs d'un même AS
        for i in range(len(routers) - 1):
            link = {
                "link_id": f"link-{link_counter}",
                "nodes": [
                    {"node_id": node_id_map[routers[i]], "adapter_number": 0, "port_number": 0},
                    {"node_id": node_id_map[routers[i + 1]], "adapter_number": 0, "port_number": 0}
                ],
                "suspend": False
            }
            gns3_project_data["topology"]["links"].append(link)
            link_counter += 1

    # Sauvegarder le fichier de projet GNS3
    with open('resultat/projet.gns3', 'w') as file:
        json.dump(gns3_project_data, file, indent=4)

    print("Fichier 'projet.gns3' généré avec succès.")

