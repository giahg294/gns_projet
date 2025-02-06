# GNS3 Network Automation Project (2024-2025)

## Description
Ce projet vise à automatiser la configuration d'un réseau composé de 5 AS interconnectés via des protocoles de routage dynamiques. L'objectif est de générer automatiquement les configurations des routeurs à partir d'un fichier de description (JSON).

## Objectifs
### 1. Configuration réseau
- Planifier l'adressage des AS.
- Configurer les interfaces loopback.
- Déployer **OSPF** dans l'AS 112 et **RIP** dans les autres AS.
- Assurer la communication entre les AS via **eBGP** et **iBGP**.

### 2. Automatisation réseau
- Définir une structure JSON décrivant l'intent du réseau.
- Générer automatiquement les configurations Cisco correspondantes.

## Architecture
Le projet repose sur un fichier de description du réseau qui spécifie :
- La topologie physique.
- Les plans d’adressage.
- Les protocoles et politiques de routage (IGP, BGP, OSPF, etc.).

## Technologies utilisées
- **GNS3** pour l'émulation réseau.
- **Python** pour la génération des configurations.
- **JSON** pour la description de l'intent du réseau.
- **Cisco IOS** pour les configurations de routeurs.

## Déploiement et Fonctionnement 
Méthode :
**Script automatique** : Déplacement des fichiers vers les bons dossiers.
Depuis le terminal avec lancer le scripe principal avec la commande "python3 main.py".
Pour observer la configuration utiliser le fichier GNS_topo_16.gns3 fourni.

## Avancement et Problèmes
- Tous les AS correctement configurés autmatiquement
- Adresses ipv6 allouées dynamiquement
- Loopback fonctionnel
- Drag and Drop bot pour dépacer les fichiers cfg dans les bons dossiers
- Début d'implémentation des BGP Policies

- Problème rencontré lors du lancement des routeurs de bordure avec l'implémentation des policies (voir fichier "problèmesR6.txt")
- Prblème de limitation de routeurs dans une AS (255 routeurs) à cause de l'allocation de ID routeur pour chaqque routeur avec un format X.X.X.X


## Auteurs
- **Yafei XU**  
- **Gia HOANG**  
