import json
from datetime import datetime

# Fonction pour lire un fichier JSON
def read_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Fonction pour générer un fichier de configuration pour chaque routeur
def generate_router_cfg(router_data, router_id, output_filename):
    with open(output_filename, 'w') as cfg_file:
        # Ajouter l'en-tête du fichier de configuration
        cfg_file.write("!\n")
        cfg_file.write(f"! Dernière modification de la configuration à {datetime.utcnow().strftime('%H:%M:%S UTC %a %b %d %Y')}\n")
        cfg_file.write("!\n")
        cfg_file.write("version 15.2\n")
        cfg_file.write("service timestamps debug datetime msec\n")
        cfg_file.write("service timestamps log datetime msec\n")
        cfg_file.write("!\n")
        
        # Configuration du nom d'hôte du routeur
        cfg_file.write(f"hostname R{router_id}\n")
        cfg_file.write("!\n")
        cfg_file.write("boot-start-marker\n")
        cfg_file.write("boot-end-marker\n")
        cfg_file.write("!\n")
        
        # Configuration des interfaces physiques et des interfaces Loopback
        for iface_type, ip_ranges in router_data['interfaces_and_addresses']['IP_ranges'].items():
            if iface_type == 'physical_interfaces':
                ip_base = "2001"
            elif iface_type == 'loopback_interfaces':
                ip_base = "2003"
            else:
                ip_base = ""
            
            # Configuration pour chaque interface
            for i, ip in enumerate(ip_ranges, 1):
                interface_name = f"FastEthernet{i}/0" if iface_type == 'physical_interfaces' else f"Loopback{i}"
                ipv6_address = f"{ip_base}::{ip}/64"
                cfg_file.write(f"interface {interface_name}\n")
                cfg_file.write(" no ip address\n")
                cfg_file.write(f" ipv6 address {ipv6_address}\n")
                cfg_file.write(" ipv6 enable\n")
                cfg_file.write(" ipv6 rip RIPng enable\n")
                cfg_file.write("!\n")
        
        # Configuration des protocoles IGP (RIP et OSPF)
        for protocol in router_data['protocols']['IGP']:
            if protocol['type'] == 'RIP':
                cfg_file.write("router rip\n")
                cfg_file.write(" version 2\n")
                for router in protocol['routers']:
                    cfg_file.write(f" network {router}\n")
                cfg_file.write("!\n")
            elif protocol['type'] == 'OSPF':
                cfg_file.write(f"router ospf 1\n")
                cfg_file.write(f" network 0.0.0.0 255.255.255.255 area {protocol['area']}\n")
                for metric in protocol['metrics']:
                    cfg_file.write(f" metric {metric[0]} {metric[1]}\n")
                cfg_file.write("!\n")
        
        # Configuration du BGP
        as_number = list(router_data['protocols']['BGP']['AS_assignments'].keys())[0]
        cfg_file.write(f"router bgp {as_number}\n")
        for session in router_data['protocols']['BGP']['sessions']:
            if session[2] == "peer":
                cfg_file.write(f" neighbor {session[1]} remote-as {as_number}\n")
            elif session[2] == "provider":
                cfg_file.write(f" neighbor {session[1]} remote-as {as_number}\n")
        cfg_file.write("!\n")
        
        # Fin du fichier de configuration
        cfg_file.write("end\n")

# Fonction pour générer les fichiers de configuration pour chaque routeur
def generate_cfg_for_routers(data):
    for router in data['network_architecture']['liens_physiques']:
        router_id = router['router']
        
        # Récupérer les données de configuration pour ce routeur
        router_data = {
            'network_architecture': data['network_architecture'],
            'interfaces_and_addresses': data['interfaces_and_addresses'],
            'protocols': data['protocols']
        }
        
        # Nom du fichier de configuration
        output_filename = f"i{router_id}_startup-config.cfg"
        
        # Générer le fichier de configuration pour ce routeur
        generate_router_cfg(router_data, router_id, output_filename)
        print(f"La configuration pour le routeur {router_id} a été générée : {output_filename}")

# Fonction principale
def main():
    # Lire les données à partir du fichier JSON
    input_filename = 'network_config.json'
    json_data = read_json(input_filename)
    
    # Générer les fichiers de configuration pour chaque routeur
    generate_cfg_for_routers(json_data)

# Exécuter la fonction principale
if __name__ == "__main__":
    main()
