import json
from datetime import datetime

# 读取 JSON 文件
def read_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# 为每个路由器生成单独的 .cfg 文件
def generate_router_cfg(router_data, router_id, output_filename):
    with open(output_filename, 'w') as cfg_file:
        # 添加头部
        cfg_file.write("!\n")
        cfg_file.write(f"! Last configuration change at {datetime.utcnow().strftime('%H:%M:%S UTC %a %b %d %Y')}\n")
        cfg_file.write("!\n")
        cfg_file.write("version 15.2\n")
        cfg_file.write("service timestamps debug datetime msec\n")
        cfg_file.write("service timestamps log datetime msec\n")
        cfg_file.write("!\n")
        
        # 配置路由器的 hostname
        cfg_file.write(f"hostname R{router_id}\n")
        cfg_file.write("!\n")
        cfg_file.write("boot-start-marker\n")
        cfg_file.write("boot-end-marker\n")
        cfg_file.write("!\n")
        
        # 配置物理接口和回环接口
        for iface_type, ip_ranges in router_data['interfaces_and_addresses']['IP_ranges'].items():
            if iface_type == 'physical_interfaces':
                ip_base = "2001"
            elif iface_type == 'loopback_interfaces':
                ip_base = "2003"
            else:
                ip_base = ""
            
            # 为每个接口配置
            for i, ip in enumerate(ip_ranges, 1):
                interface_name = f"FastEthernet{i}/0" if iface_type == 'physical_interfaces' else f"Loopback{i}"
                ipv6_address = f"{ip_base}::{ip}/64"
                cfg_file.write(f"interface {interface_name}\n")
                cfg_file.write(" no ip address\n")
                cfg_file.write(f" ipv6 address {ipv6_address}\n")
                cfg_file.write(" ipv6 enable\n")
                cfg_file.write(" ipv6 rip RIPng enable\n")
                cfg_file.write("!\n")
        
        # 配置 IGP（RIP 和 OSPF）
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
        
        # 配置 BGP
        as_number = list(router_data['protocols']['BGP']['AS_assignments'].keys())[0]
        cfg_file.write(f"router bgp {as_number}\n")
        for session in router_data['protocols']['BGP']['sessions']:
            if session[2] == "peer":
                cfg_file.write(f" neighbor {session[1]} remote-as {as_number}\n")
            elif session[2] == "provider":
                cfg_file.write(f" neighbor {session[1]} remote-as {as_number}\n")
        cfg_file.write("!\n")
        
        # 文件结束
        cfg_file.write("end\n")

# 为每个路由器生成配置文件
def generate_cfg_for_routers(data):
    for router in data['network_architecture']['liens_physiques']:
        router_id = router['router']
        
        # 获取当前路由器的配置
        router_data = {
            'network_architecture': data['network_architecture'],
            'interfaces_and_addresses': data['interfaces_and_addresses'],
            'protocols': data['protocols']
        }
        
        # 设置文件名
        output_filename = f"i{router_id}_startup-config.cfg"
        
        # 为当前路由器生成配置文件
        generate_router_cfg(router_data, router_id, output_filename)
        print(f"Configuration for router {router_id} has been generated: {output_filename}")

# 主程序
def main():
    # 读取 JSON 文件
    input_filename = 'network_intents.json'
    json_data = read_json(input_filename)
    
    # 为每个路由器生成单独的配置文件
    generate_cfg_for_routers(json_data)

# 执行主程序
if __name__ == "__main__":
    main()
