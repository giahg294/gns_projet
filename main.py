# Reste a voir::::: 
import json 
import os 
from allocate_addres import * 
from configuration import * 


# 定义一个函数，用于将文件从源目录移动到目标目录，并覆盖目标目录中同名的文件
def move_and_overwrite(source_file, target_directory):
    target_file = os.path.join(target_directory, os.path.basename(source_file))  # 生成目标文件路径
    shutil.move(source_file, target_file)  # 移动文件并覆盖目标文件


# 打开并读取 JSON 文件，加载数据
with open('14routers.json', 'r') as file:
    data = json.load(file)

# 将 JSON 数据中的 AS 信息提取出来，创建 AS 类的实例，存入 all_as 列表
all_as = [AS(as_info['number'], as_info['IP_range'], as_info['loopback_range'], as_info['protocol'], as_info['routers']) 
          for as_info in data['AS']]

# 创建一个字典 as_mapping，用于存储每个路由器所属的 AS 编号
as_mapping = {}
for as_index in all_as:  # 遍历所有 AS 实例
    for router in as_index.routers:  # 遍历 AS 中的所有路由器
        as_mapping[router.name] = as_index.number  # 将路由器名称映射到所属的 AS 编号

# 创建一个包含所有路由器的列表 all_routers
all_routers = [router for as_index in all_as for router in as_index.routers]

# 使用路由器列表和 AS 映射生成连接矩阵的名称
connections_matrix_name = generate_connections_matrix_name(all_routers, as_mapping)
print(connections_matrix_name)  # 打印连接矩阵名称

# 使用路由器列表和 AS 映射生成连接矩阵
connections_matrix = generate_connections_matrix(all_routers, as_mapping)
print(connections_matrix)  # 打印连接矩阵

# 生成路由器的相关信息字典
routers_info = generate_routers_dict(all_as)

# 初始化连接类型计数器
connection_counts = {"111": 0, "112": 0, "border": 0}
# 遍历连接矩阵，统计不同类型连接的数量
for conn in connections_matrix:
    connection_counts[conn[1]] += 1


# 定义一个空列表，用于存储所有生成的源文件
source_file = []

# 定义目标目录的列表: 14 routers
target_directory = [
    'resultat/project-files/dynamips/5b1ce96a-83fb-42cd-bb74-2f73c9b5e22b',
    'resultat/project-files/dynamips/2af24f68-e50a-465a-bc73-d92bc75d5bc9',
    'resultat/project-files/dynamips/8f42c9e7-29d7-4f90-8b65-0a267c3807d8',
    'resultat/project-files/dynamips/90fa75c6-2d30-460b-bcde-0fd7f687e13d',
    'resultat/project-files/dynamips/a2b478b3-1c7d-4fe3-b65a-9176ca7b56a2',
    'resultat/project-files/dynamips/c9e7423a-bef9-41d9-8d79-bd36c13f4135',
    'resultat/project-files/dynamips/98d4ed54-d28b-47f2-bc68-90fc0728b300',
    'resultat/project-files/dynamips/3bfb2ca1-93f3-4d67-8bfa-fd81a3a1c953',
    'resultat/project-files/dynamips/67d4f70d-5a68-463f-9403-cb94b883924b',
    'resultat/project-files/dynamips/23b5ecaf-8be9-4e5e-86f3-c49fe5fd9533',
    'resultat/project-files/dynamips/0a0d2352-b2e6-4e0d-a717-1f4728c56f6a',
    'resultat/project-files/dynamips/7b6d5e47-9238-45d2-bfa5-7463b2300eb4',
    'resultat/project-files/dynamips/41096a2f-1955-4b16-b574-d0842c1b03a0',
    'resultat/project-files/dynamips/34b57372-99e1-4ec9-bb80-586af23c24c1'
]

# 遍历所有 AS 和 AS 中的路由器，为每个路由器生成接口地址
for as_index in all_as:
    for router in as_index.routers:
        generate_interface_addresses(router.name, router.interfaces, connections_matrix, connection_counts)

# 遍历所有 AS 和 AS 中的路由器，为每个路由器生成配置文件
for as_index in all_as:
    for router in as_index.routers:
        # 生成路由器的 loopback 地址
        router_loopback = generate_loopback(router.name, as_index.loopback_range)
        # 生成路由器的 ID
        router_id = generate_router_id(router.name)
        config = []  # 创建一个空的配置列表
        # 依次添加配置头、loopback 配置、接口配置、BGP 配置和配置尾
        config.extend(config_head(router.name))
        config.extend(config_loopback(router_loopback, as_index.protocol))
        config.extend(config_interface(router.interfaces, as_index.protocol, router, connections_matrix_name))
        config.extend(config_bgp(router, router_id, all_routers, connections_matrix_name, routers_info))
        config.extend(config_end(as_index.protocol, router_id, router, connections_matrix_name))
        
        # 将配置写入文件
        with open(f"i{router.name[1:]}_startup-config.cfg", 'w') as file:
            file.write('\n'.join(config))  # 写入配置内容
            source_file.append(f"i{router.name[1:]}_startup-config.cfg")  # 将文件名添加到 source_file 列表中

