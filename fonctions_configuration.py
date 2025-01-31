from address_allocator import *
import ipaddress

# Configurer l'en-tête du fichier
def config_head(name):
    # Définir la configuration de l'en-tête du fichier
    config = [
        "!\r"*3,
        "!",
        "version 15.2",  # Version du logiciel
        "service timestamps debug datetime msec",  # Activer les horodatages pour le débogage
        "service timestamps log datetime msec",  # Activer les horodatages pour les journaux
        "!",
        f"hostname {name}",  # Définir le nom d'hôte du routeur
        "!",
        "boot-start-marker",  # Marqueur de début de démarrage
        "boot-end-marker",  # Marqueur de fin de démarrage
        "!\r"*2 + "!",
        "no aaa new-model",  # Désactiver le nouveau modèle AAA
        "no ip icmp rate-limit unreachable",  # Désactiver la limitation du taux ICMP
        "ip cef",  # Activer la CEF (Cisco Express Forwarding)
        "!\r"*5 + "!",
        "no ip domain lookup",  # Désactiver la recherche de domaine IP
        "ipv6 unicast-routing",  # Activer le routage unicast IPv6
        "ipv6 cef",  # Activer la CEF pour IPv6
        "!\r!",
        "multilink bundle-name authenticated",  # Définir le nom du groupe multilink
        "!\r"*8 + "!",
        "ip tcp synwait-time 5",  # Définir le délai d'attente TCP SYN
        "!\r"*11 + "!",
    ]
    return config


# Configure Loopback Interface
def config_loopback(ip_loopback, protocol):
    # Configurer l'interface Loopback
    config = []
    config.append("interface Loopback0")
    config.append(" no ip address")  # Désactiver l'adresse IPv4
    config.append(f" ipv6 address {ip_loopback}")  # Configurer l'adresse IPv6
    config.append(" ipv6 enable")  # Activer IPv6 sur l'interface

    if protocol == "RIP":
        config.append(" ipv6 rip ng enable")  # Activer RIP pour IPv6
    if protocol == "OSPF":
        config.append(" ipv6 ospf 1 area 0")  # Associer l'interface à une zone OSPF

    config.append("!")
    return config


# Configure each interface
def config_interface(interfaces, protocol, router, connections_matrix_name):
    # Configurer chaque interface réseau
    config = []
    for interface in interfaces:
        config.append(f"interface {interface['name']}")  # Nom de l'interface

        # if protocol == "OSPF":
        #     if interface['cost'] != 0:
        #         # Calculer la nouvelle bande passante en fonction du coût OSPF
        #         new_bandwidth = round(100000 / interface['cost'])
        #         config.append(f"bandwidth {new_bandwidth}")  # Définir la bande passante

        config.append(" no ip address")  # Désactiver IPv4

        if interface['neighbor'] == "None":
            # Si l'interface n'a pas de voisin, la désactiver
            config.append(" shutdown")

            if interface['name'] == "FastEthernet0/0":
                config.append(" duplex full")  # Configurer le mode duplex
            else:
                config.append(" negotiation auto")  # Activer la négociation automatique
        else:
            # Configurer les interfaces avec un voisin
            if interface['name'] == "FastEthernet0/0":
                config.append(" duplex full")
            else:
                config.append(" negotiation auto")

            ipv6_address = interface.get('ipv6_address', '')  # Obtenir l'adresse IPv6 de l'interface
            if ipv6_address:
                config.append(f" ipv6 address {ipv6_address}")  # Associer l'adresse IPv6
                config.append(" ipv6 enable")  # Activer IPv6

                if protocol == "RIP" and not ipv6_address.startswith("2001:192:170:"):
                    config.append(" ipv6 rip ng enable")  # Activer RIP si applicable
                elif protocol == "OSPF":
                    config.append(" ipv6 ospf 1 area 0")  # Associer à une zone OSPF

        if protocol == "OSPF":
            config.append("!")
            config.append("router ospf 1")

        config.append("!")

    return config


# Configure bgp neighbor
def config_bgp(router, router_id, routers, connections_matrix_name, routers_dict):
    # Configurer les voisins BGP
    config = []
    current_as = routers_dict[router.name]['AS']  # Numéro d'AS actuel
    neighbor_liste = []

    config.append(f"router bgp {current_as}")  # Définir l'AS pour BGP
    config.append(f" bgp router-id {router_id}")  # Identifier le routeur
    config.append(" bgp log-neighbor-changes")  # Journaliser les modifications des voisins
    config.append(" no bgp default ipv4-unicast")  # Désactiver le trafic IPv4 par défaut

    if router.router_type == "eBGP":
        neighbor_ip = None

        for elem in connections_matrix_name:
            ((r1, r2), state) = elem

            if state == 'border':
                if router.name == r1:
                    neighbor = r2
                elif router.name == r2:
                    neighbor = r1
                else:
                    neighbor = None

                if neighbor:
                    for routeur in routers:
                        if routeur.name == neighbor:
                            for interface in routeur.interfaces:
                                if interface['neighbor'] == router.name:
                                    neighbor_ip = interface.get('ipv6_address', '')
                                    break

                    if neighbor_ip:
                        as_number = routers_dict[neighbor]['AS']  # Obtenir l'AS du voisin
                        config.append(f" neighbor {neighbor_ip[:-3]} remote-as {as_number}")
                        neighbor_liste.append(neighbor_ip[:-3])

    for routeur_name, routeur_info in routers_dict.items():
        if routeur_name != router.name and routeur_info['AS'] == current_as:
            # Configurer les voisins internes
            config.append(f" neighbor {routeur_info['loopback'][:-4]} remote-as {routeur_info['AS']}")
            config.append(f" neighbor {routeur_info['loopback'][:-4]} update-source Loopback0")
            neighbor_liste.append(routeur_info['loopback'][:-4])

    config.append(" !")
    config.append(" address-family ipv4")  # Configurer la famille d'adresses IPv4
    config.append(" exit-address-family")
    config.append(" !")
    config.append(" address-family ipv6")  # Configurer la famille d'adresses IPv6

    # Annoncer tous les sous-réseaux d'un AS
    liste = list(routers_dict.keys())
    if router.name == liste[5] or router.name == liste[6] or router.name == liste[7] or router.name == liste[8]:
        networks = []
        if current_as == "111":
            for routeur in routers:
                if routeur.name in ["R1","R2","R3","R4","R5"]:
                    for interface in routeur.interfaces:
                        ip_addr = interface.get('ipv6_address', '')
                        if ip_addr:
                            try:
                                network = ipaddress.IPv6Network(ip_addr, strict=False)
                                if network not in networks : 
                                    networks.append(network)
                            except ValueError:
                                print(f"Invalid IPv6 addresse: {ip_addr}")
        else:
            for routeur in routers:
                if routeur.name in ["R10","R11","R12","R13","R14"]:
                    for interface in routeur.interfaces:
                        ip_addr = interface.get('ipv6_address', '')
                        if ip_addr:
                            try:
                                network = ipaddress.IPv6Network(ip_addr, strict=False)
                                if network not in networks : 
                                    networks.append(network)
                            except ValueError:
                                print(f"Invalid IPv6 addresse: {ip_addr}")

        # Trier les sous-réseaux
        networks.sort(key=lambda net: (net.network_address, net.prefixlen))

        for network in networks:
            config.append(f"  network {str(network)}")  # Ajouter les sous-réseaux à la configuration

    # Activer les voisins IPv6
    for ip_neighbor in neighbor_liste:
        config.append(f"  neighbor {ip_neighbor} activate")

    config.append(" exit-address-family")
    config.append("!")

    return config


# Configure end of file
def config_end(protocol, router_id, router, connections_matrix_name):
    # Configurer la fin du fichier
    config = [
        "ip forward-protocol nd",
        "!\r!",
        "no ip http server",  # Désactiver le serveur HTTP
        "no ip http secure-server",  # Désactiver le serveur HTTP sécurisé
        "!"
    ]

    # Configurer le protocole
    if protocol == "RIP":
        config.append("ipv6 router rip ng")  # Configurer RIP
        config.append(" redistribute connected")  # Redistribuer les routes connectées
    if protocol == "OSPF":
        config.append("ipv6 router ospf 1")  # Configurer OSPF
        config.append(f" router-id {router_id}")  # Définir l'ID du routeur

    # Configurer l'interface passive pour OSPF et eBGP
    if protocol == "OSPF" and router.router_type == "eBGP":
        interface_name = None
        
        for elem in connections_matrix_name:
            ((r1, r2), state) = elem

            if state == 'border':
                if router.name == r1:
                    neighbor = r2
                elif router.name == r2:
                    neighbor = r1
                else:
                    neighbor = None

                if neighbor:
                    for interface in router.interfaces:
                        if interface['neighbor'] == neighbor:
                            interface_name = interface['name']
                            break
            
                    config.append(f" passive-interface {interface_name}")  # Définir l'interface comme passive

    part = [
        "!\r"*3 + "!",
        "control-plane",
        "!\r!",
        "line con 0",
        " exec-timeout 0 0",
        " privilege level 15",
        " logging synchronous",
        " stopbits 1",
        "line aux 0",
        " exec-timeout 0 0",
        " privilege level 15",
        " logging synchronous",
        " stopbits 1",
        "line vty 0 4",
        " login",
        "!\r!",
        "end\r"
    ]

    config.extend(part)

    return config
