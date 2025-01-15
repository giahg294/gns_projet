# pip install gns3fy
>>> import gns3fy

# Define the server object to establish the connection
>>> gns3_server = gns3fy.Gns3Connector("http://<server address>:3080")

# Define the lab you want to load and assign the server connector
>>> lab = gns3fy.Project(name="API_TEST", connector=gns3_server)

# Retrieve its information and display
>>> lab.get()
>>> print(lab)
"Project(project_id='4b21dfb3-675a-4efa-8613-2f7fb32e76fe', name='API_TEST', status='opened', ...)"

# Access the project attributes
>>> print(f"Name: {lab.name} -- Status: {lab.status} -- Is auto_closed?: {lab.auto_close}")
"Name: API_TEST -- Status: closed -- Is auto_closed?: False"

# Open the project
>>> lab.open()
>>> lab.status
opened

# Verify the stats
>>> lab.stats
{'drawings': 0, 'links': 4, 'nodes': 6, 'snapshots': 0}

# List the names and status of all the nodes in the project
>>> for node in lab.nodes:
...    print(f"Node: {node.name} -- Node Type: {node.node_type} -- Status: {node.status}")

"Node: Ethernetswitch-1 -- Node Type: ethernet_switch -- Status: started"
...










import json
import random

# 读取网络意图文件
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# 生成BGP配置
def generate_bgp_config(as_number, routers):
    config = []
    for router in routers:
        router_name = router['hostname']
        router_bgp_config = f"router bgp {as_number}\n"
        router_bgp_config += f"bgp router-id {router['loopback_ip']}\n"
        
        for peer in router['bgp_peers']:
            peer_ip = peer['ip']
            peer_as = peer['as']
            router_bgp_config += f"neighbor {peer_ip} remote-as {peer_as}\n"
        
        config.append((router_name, router_bgp_config))
    
    return config

# 生成接口配置
def generate_interface_config(interfaces, ip_range):
    config = []
    for interface in interfaces:
        if interface['type'] == 'physical':
            ip_address = f"{ip_range}.1"  # 假设自动分配的IP
            ip_range += 1
        else:
            ip_address = f"{ip_range}.2"  # 假设自动分配的IP
            ip_range += 1
        
        interface_config = f"interface {interface['name']}\n"
        interface_config += f"ip address {ip_address} 255.255.255.0\n"
        interface_config += f"no shutdown\n"
        config.append(interface_config)
    
    return config, ip_range

# 生成路由器配置
def generate_router_configs(data):
    configs = []
    
    for as_data in data['network']['autonomous_systems']:
        as_number = as_data['as_number']
        routers = as_data['routers']
        
        # 生成BGP配置
        bgp_configs = generate_bgp_config(as_number, routers)
        
        # 生成接口配置
        ip_range = 192168000  # 假设起始IP地址范围
        for router in routers:
            interfaces = router['interfaces']
            interface_configs, ip_range = generate_interface_config(interfaces, ip_range)
            
            configs.append(f"hostname {router['hostname']}")
            configs.extend(interface_configs)
            configs.extend([bgp_config for router_name, bgp_config in bgp_configs if router_name == router['hostname']])
    
    return "\n".join(configs)

# 主函数
if __name__ == "__main__":
    # 加载意图文件
    json_file = "network_intents.json"  # 路径可以根据实际情况调整
    data = load_json(json_file)
    
    # 生成路由器配置
    router_configs = generate_router_configs(data)
    
    # 保存生成的配置文件
    with open('generated_router_config.txt', 'w') as f:
        f.write(router_configs)
    
    print("Router configurations generated successfully!")
