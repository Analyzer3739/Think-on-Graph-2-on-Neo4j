
from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor, as_completed

from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import numpy as np
import re
import json
import time
from neo4j import GraphDatabase
from concurrent.futures import ThreadPoolExecutor, as_completed

class Neo4jQueryClient:
    def __init__(self, server_addrs, user, password):
        """
        初始化 Neo4j 客户端
        :param server_addrs: Neo4j 服务器地址列表
        :param user: 用户名
        :param password: 密码
        """
        self.drivers = []
        for uri in server_addrs:
            try:
                # 确保 uri 是字符串
                if not isinstance(uri, str):
                    print(f"警告: 非字符串URI: {uri}, 跳过")
                    continue
                    
                driver = GraphDatabase.driver(uri, auth=(user, password))
                self.drivers.append(driver)
                print(f"成功连接到服务器: {uri}")
            except Exception as e:
                print(f"无法连接到 {uri}: {str(e)}")
        
        # 设置主驱动（第一个可用驱动）
        self.main_driver = self.drivers[0] if self.drivers else None
    
    def close(self):
        """关闭所有数据库连接"""
        for driver in self.drivers:
            try:
                driver.close()
            except:
                pass
        print("所有数据库连接已关闭")
    
    def query_all(self, cql, parameters=None):
        """
        在所有服务器上执行查询并合并结果
        :param cql: Cypher 查询语句
        :param parameters: 查询参数 (可选)
        :return: 合并后的结果集
        """
        if parameters is None:
            parameters = {}

        # if parameters:
        #     print(f"查询参数: {parameters}")

        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=len(self.drivers)) as executor:
            futures = [executor.submit(self._execute_query, driver, cql, parameters) for driver in self.drivers]
            
            for future in as_completed(futures):
                try:
                    result_list = future.result()
                    results.extend(result_list)
                except Exception as e:
                    print(f"查询失败: {str(e)}")
        
        duration = time.time() - start_time
        # print(f"查询完成，耗时: {duration:.2f}秒，结果数: {len(results)}")
        return results if results else "未找到结果!"
    
    def _execute_query(self, driver, cql, parameters):
        """在单个服务器上执行查询"""
        try:
            with driver.session() as session:
                result = session.run(cql, parameters)
                # 直接返回字典列表，而不是尝试转换为元组
                return [dict(record) for record in result]
        except Exception as e:
            print(f"查询执行失败: {str(e)}")
            return []
    
    def vector_query_nodes(self, index_name1, index_name2, top_k, embedding):
        """
        在主服务器上执行向量查询
        :param index_name: 向量索引名称
        :param top_k: 返回结果数量
        :param embedding: 查询向量
        :return: 实体列表 (字典数组)
        """
        if not self.main_driver:
            print("⚠️ 没有可用的数据库连接")
            return []
        
        try:
            with self.main_driver.session() as session:
                query = """
                CALL {
                    CALL db.index.vector.queryNodes($index_name1, $top_k, $embedding)
                    YIELD node, score
                    RETURN node, score
                    UNION
                    CALL db.index.vector.queryNodes($index_name2, $top_k, $embedding)
                    YIELD node, score
                    RETURN node, score
                }
                RETURN COALESCE(node.name, node.title) AS entity, score
                ORDER BY score DESC
                """
                
                #print(f"执行向量查询: {query}")
                result = session.run(query, {
                    "index_name1": index_name1,
                    "index_name2": index_name2,
                    "top_k": top_k,
                    "embedding": embedding
                })
                # print(result)
                # 确保结果按预期结构返回（字典列表）
                entities = []
                for record in result:
                    # 将记录转换为字典格式
                    record_dict = dict(record.items())
                    entity = record_dict.get("entity")
                    score = record_dict.get("score")
                    
                    if entity and score:
                        print(f"实体: {entity}, 相似度: {score:.4f}")
                        entities.append(entity)
                    else:
                        print(f"⚠️ 无效记录格式: {record}")
                
                print(f"找到 {len(entities)} 个相关实体")
                return entities
        except Exception as e:
            import traceback
            print(f"向量查询失败: {str(e)}")
            print(f"错误详情:\n{traceback.format_exc()}")
            return []

    def get_index_status(self, index_name):
        """
        获取索引状态
        :param index_name: 索引名称
        :return: 索引状态信息
        """
        if not self.main_driver:
            return None
        
        try:
            with self.main_driver.session() as session:
                result = session.run("""
                    SHOW INDEXES 
                    YIELD name, type, state, labelsOrTypes, properties
                    WHERE name = $index_name
                    RETURN state, labelsOrTypes, properties
                """, index_name=index_name)
                
                return result.single()
        except Exception as e:
            print(f"获取索引状态失败: {str(e)}")
            return None

def get_entities_from_neo4j(n4j_client, question, emb_model, top_k=5):
    """
    通过问题向量匹配 Neo4j 实体
    
    参数:
        n4j_client: Neo4jQueryClient 实例
        question: 问题文本
        emb_model: 嵌入模型
        top_k: 返回的实体数量
    """
    try:
        # 生成问题向量 - 使用与索引创建相同的编码方式
        question_embedding = emb_model.encode(question).tolist()
        #print(f"问题向量维度: {len(question_embedding)}")
    except Exception as e:
        print(f"向量生成失败: {str(e)}")
        return ["默认实体"]
    
    # 使用与创建时相同的索引名称
    index_name1 = "entity_vector_idx"
    index_name2 = "section_vector_idx"
    
    # 执行向量查询
    entities = n4j_client.vector_query_nodes(index_name1, index_name2, top_k, question_embedding)
    
    # 如果没有结果，检查索引状态
    # if len(entities) == 0:
    #     print("⚠️ 未找到实体，检查索引状态...")
    #     index_status = n4j_client.get_index_status(index_name)
        
    #     if index_status:
    #         print(f"索引状态: {index_status['state']}")
    #         print(f"索引标签: {index_status['labelsOrTypes']}")
    #         print(f"索引属性: {index_status['properties']}")
    #     else:
    #         print(f"索引 '{index_name}' 不存在")
    
    return entities

def neo4j_relation_search(entity_name, pre_relations, depth, n4j_client):
    """在Neo4j中搜索与实体相关的关系"""
    # 构建Cypher查询
    cql = """
    MATCH (e:Entity {label_name: $entity_name})-[r]->(n)
    RETURN type(r) AS relation_type, n.label_name AS target_entity
    """
    
    # 执行查询
    results = n4j_client.query_all(cql, parameters={"entity_name": entity_name})
    
    # 格式化结果
    relations = []
    for record in results:
        relations.append({
            "source_entity": entity_name,
            "relation_type": record["relation_type"],
            "target_entity": record["target_entity"],
            "depth": depth
        })
    
    return relations

def neo4j_relation_search_prune(entity_name, pre_relations, question, depth, n4j_client, emb_model):
    """带剪枝的关系搜索"""
    # 1. 获取所有可能关系
    all_relations = neo4j_relation_search(entity_name, pre_relations, depth, n4j_client)
    
    # 2. 计算关系与问题的相关性
    relation_texts = [f"{rel['source_entity']} {rel['relation_type']} {rel['target_entity']}" 
                      for rel in all_relations]
    
    # 3. 使用嵌入模型计算相似度
    question_embedding = emb_model.encode(question)
    relation_embeddings = emb_model.encode(relation_texts)
    similarities = np.dot(relation_embeddings, question_embedding) / (
        np.linalg.norm(relation_embeddings, axis=1) * np.linalg.norm(question_embedding)
    )
    
    # 4. 筛选最相关的关系
    threshold = 0.5  # 可配置阈值
    pruned_relations = []
    for i, rel in enumerate(all_relations):
        if similarities[i] > threshold:
            rel["score"] = similarities[i]
            pruned_relations.append(rel)
    
    return pruned_relations