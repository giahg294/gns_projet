import os
import shutil

path = "/mnt/c/Users/giaho/Documents/3A/GNS"
source = path + "/GNS_code/gns_projet/"
destination = path + "/GNS_topo/GNS_topo_14/project-files/dynamips"

# Définir une fonction pour déplacer un fichier du répertoire source vers le répertoire cible, en écrasant les fichiers portant le même nom dans le répertoire cible
def move_and_overwrite(source_file, target_directory):
    target_file = os.path.join(target_directory, os.path.basename(source_file))  # Générer le chemin du fichier cible
    # shutil.move(source_file, target_file)  # Déplacer le fichier et écraser le fichier cible
    print(target_file)
    if not os.path.exists(target_file):
        shutil.move(source_file, target_directory)
        print(f'{source_file} déplacé avec succès')
    else:
        print(f'{source_file} existe déjà')


# Définir la liste des répertoires cibles : 14 routers
target_directory = [
    "/6f3ff8e8-983a-43bc-9284-911bf78bc71f/configs", # R1
    "/57250c95-d1a4-401a-b812-81b461973c0f/configs", # R2
    "/837c0d00-50d9-41be-9631-c3fb3129a53b/configs", # R3
    "/68ad9717-3e6a-4c90-91d7-c30acd723d82/configs", # R4
    "/2f4046af-a5e6-4263-9fd9-dc84ef7913c4/configs", # R5
    "/75e79790-3ffa-4ba5-813a-893f296f2504/configs", # R6
    "/b2789722-dcaa-4206-9f5a-e7c1d70cd21b/configs", # R7
    "/a2960629-2a83-4559-8478-5ee6a403e87a/configs", # R8
    "/6c28efad-040f-4e13-9266-fafdc12229ce/configs", # R9
    "/85920f6a-1a0e-4304-bb8a-a49742f58b81/configs", # R10
    "/e5e90cab-a67f-464a-a374-671a0cc7baa6/configs", # R11
    "/ceb29b58-3e84-4da3-94d8-5486eb3b1a2a/configs", # R12
    "/d9da0c63-4491-40c3-9898-23a258a45eab/configs", # R13
    "/9ceedcee-8c91-431c-8c7a-e013bbe5df6b/configs", # R14
    ]

def drag_file(i, fichiers_config):
    file = source + fichiers_config[i]
    target_file = destination + target_directory[i] + "/" + fichiers_config[i]
    shutil.move(file,target_file)
    print(f"le bot s'est occupé {fichiers_config[i]} avec succès.")

