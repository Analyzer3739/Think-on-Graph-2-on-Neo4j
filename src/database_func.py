import time,openai,json,random,heapq,math
from utils import *
from search import *
from openai import OpenAI


def run_llm_json(prompt, temperature, max_tokens, openai_api_keys, args, engine="llama3"):
    if "llama" in engine.lower():
        openai_api_key = "EMPTY"
        openai_api_base = "http://127.0.0.1:11434/v1"

        client = OpenAI(
            api_key=openai_api_key,
            base_url=openai_api_base,
        )

        models = client.models.list()
        engine = models.data[0].id
        print("USING LLM: ",engine)
        res_format = {"type": "text"}
    else:
        client = openai.OpenAI(api_key=openai_api_keys, base_url="")
        res_format = {"type": "json_object"}

    if 'llama' in engine.lower():
        if "fin" in args.dataset:
            sys_prompt = '''你是一个专业的中文金融助手，被设计用于以JSON形式回答问题.'''
        else:
            sys_prompt = '''You are a helpful assistant designed to output JSON.'''
        messages = [{"role": "system", "content": sys_prompt}]
        message_prompt = {"role": "user", "content": prompt}
        messages.append(message_prompt)
    else:
        sys_prompt = '''You are a helpful assistant designed to output JSON.'''
        messages = [{"role": "system", "content": sys_prompt}]
        message_prompt = {"role": "user", "content": prompt}
        messages.append(message_prompt)

    f = 3
    while (f > 0):
        try:
            response = client.chat.completions.create(
                model=engine,
                response_format=res_format,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                frequency_penalty=0,
                presence_penalty=0)
            result = response.choices[0].message.content
            f = -1
        except Exception as e:
            print(e)
            f -= 1
            time.sleep(5)

    return result


def topic_e_prune(question, entities, args):
    def extract_output(text):

        match = re.search(r'\{\s*"selected_entities"\s*:\s*\[.*?\]\s*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        else:
            return ""
    def construct_topic_prune_prompt(question, entities):
        entities_json_string = json.dumps(entities)
        prompt = 'question: ' + question + '\ntopic entities:\n' + entities_json_string + '\nOutput:'
        return prompt


    prompt = construct_topic_prune_prompt(question, entities)
    #print(prompt)
    prompt = topic_prune_demos_new + '\n' + prompt
    results = run_llm_json(prompt, args.temperature_exploration, args.max_length, args.opeani_api_keys, args)
    if 'llama' in args.LLM_type:
        json_str = extract_output(results).strip()
        try:
            results = json.loads(json_str)
        except ValueError:
            print("Entity prune failed, output original entities",json_str,"11",results)
            return entities
    else:
        try:
            results = json.loads(results)
        except Exception as e:
            print("Entity prune failed, output original entities. Error result:{}. Error Info{}".format(results, e))
            return entities

    if isinstance(results, dict) and "selected_entities" in results:
        selected_entities = results["selected_entities"]
        print('选择实体:\n' + ', '.join(selected_entities))
        return selected_entities
    else:
        print("实体剪枝失败，返回原始实体")
    return entities




docs_folder='docs_pages/'

def get_original_text(n4j_client, entity_dict: dict) -> str:
    """从 Neo4j 获取实体原始文本"""
    # 1. 构建Cypher查询 - 使用name属性匹配
    cql = """
    MATCH (e) 
    WHERE 
        ("Entity" IN labels(e) OR "Section" IN labels(e)) AND 
        (e.name = $name OR e.title = $name)  // 支持 name 或 title 属性
    RETURN coalesce(e.content, '') AS text
    """
    
    # 2. 执行查询并获取结果
    try:
        # 使用参数化查询
        results = n4j_client.query_all(cql, parameters={
            "name": entity_dict["name"]  # 使用传入的名称作为name
        })
        
        if results and results != "未找到结果!":
            # 拼接所有结果的文本
            chunk = " ".join(record["text"] for record in results)
            print("entity name:", entity_dict["name"], '\nentity docs:', chunk[:30] + ("..." if len(chunk) > 30 else ""))
            return chunk
        return "Not Found!"
    except Exception as e:
        print(f"Query failed for {entity_dict['name']}: {str(e)}")
        return "Not Found!"
    
def transform_relation(n4j_relation):
    relation_without_prefix = n4j_relation.replace("n4j.relation.", "").replace("_", " ")
    return relation_without_prefix

def construct_relation_prune_prompt(question, entity_name, total_relations, args):
    return extract_relation_prompt_wiki % (args.width)+question+'\nTopic Entity: '+entity_name+ '\nRelations:\n'+'\n'.join([f"{i}. {item}" for i, item in enumerate(total_relations, start=1)])+'Answer:\n'

def clean_relations(string, entity_name, head_relations,args):
    pattern = r"{\s*(?P<relation>[^()]+)\s+\(Score:\s+(?P<score>[0-9.]+)\)}"
    relations=[]
    for match in re.finditer(pattern, string):
        n4j_relation = match.group("relation").strip()
        n4j_relation = transform_relation(n4j_relation)
        if ';' in n4j_relation:
            continue
        score = match.group("score")
        if not n4j_relation or not score:
            return False, "output uncompleted.."
        try:
            score = float(score)
        except ValueError:
            return False, "Invalid score"
        if n4j_relation in head_relations:
            relations.append({"entity_name": entity_name, "relation": n4j_relation, "score": score, "head": True})
        else:
            relations.append({"entity_name": entity_name, "relation": n4j_relation, "score": score, "head": False})

    if not relations:
        return False, "No relations found"
    filtered_relations = [x for x in relations if x['score'] >= 0.2]
    if not filtered_relations:
        return False, "No relations found"
    sorted_data = sorted(filtered_relations, key=lambda x: x['score'], reverse=True)[0:args.width]
    return True, sorted_data

def construct_all_relation_prune_prompt(question, all_entity_relations, args):
    temp_prompt = extract_all_relation_prompt_wiki_cn % (args.width, args.width, args.width) + question
    for i, entity_relations in enumerate(all_entity_relations.values(), start=1):
        if len(entity_relations) > 0:
            temp_prompt += ('\nEntity %s: ' % i + entity_relations[0]['entity_name'] + '\nAvailable Relations:\n' +
                            '\n'.join([f"{i}. {item['relation']}" for i, item in enumerate(entity_relations, start=1)]))
    return temp_prompt + '\nAnswer:'

def clean_relation_all_e(results, all_entity_relations):
    # 预处理标准化数据
    normalized_rels = {}
    for k, v in all_entity_relations.items():
        key = k.lower().strip()
        normalized_rels[key] = [{
            'relation': r['relation'].lower().strip(),
            'head': r['head']
        } for r in v]
    
    entities_info = []
    entity_sections = re.split(r"Entity\s?\d+:", results)[1:]
    
    for section in entity_sections:
        section = section.strip()
        # 改进的实体名提取
        entity_match = re.search(r"([^{}\n]+?)\s*(?:{.*?)?$", section)
        if not entity_match:
            continue
        entity_name = entity_match.group(1).strip().lower()
        
        if entity_name not in normalized_rels:
            print(f"实体名 '{entity_name}' 不匹配可选项: {list(normalized_rels.keys())}")
            continue
            
        # 改进的关系匹配模式
        relation_pattern = r"(?:{|\{)\s*(?P<relation>[^{}]+?)\s+\(Score:\s+(?P<score>[0-9.]+)\)(?:}|\})"
        for match in re.finditer(relation_pattern, section):
            raw_relation = match.group("relation").strip()
            relation_name = transform_relation(raw_relation).lower()
            score = float(match.group("score"))
            
            # 在标准化关系中查找
            found = [r for r in normalized_rels[entity_name] 
                     if r["relation"] == relation_name]
            
            if not found:
                print(f"关系不匹配: '{relation_name}' (原始: '{raw_relation}') "
                      f"实体: '{entity_name}' 可选项: {normalized_rels[entity_name]}")
                continue
                
            entities_info.append({
                "entity_name": entity_name,
                "relation": relation_name,
                "score": score,
                "head": found[0]["head"]
            })
    
    if not entities_info:
        return False, "未找到任何关系"
    
    seen = set()
    temp_list = []
    for item in entities_info:
        entity_name = item['entity_name']
        relation = item['relation']
        if (entity_name, relation) in seen:
            continue
        seen.add((entity_name, relation))
        temp_list.append(item)
    return True, temp_list


def relation_prune_all(all_entity_relations, question, args):
    prompt = construct_all_relation_prune_prompt(question, all_entity_relations, args)
    print("22",prompt)
    result = run_llm(prompt, args.temperature_exploration, args.max_length, args.opeani_api_keys, args.LLM_type_rp)
    flag, retrieve_relations_with_scores = clean_relation_all_e(result, all_entity_relations)
    print("11",result)
    if flag:
        return retrieve_relations_with_scores
    else:
        return []


def relation_search_prune(entity_name, pre_relations, pre_head, question, args, n4j_client):

    head_query = """
    MATCH (e:Entity {name: $entity_name})-[r]->(o)
    RETURN DISTINCT type(r) AS relation_type, 'head' AS direction
    """
    
    tail_query = """
    MATCH (e:Entity {name: $entity_name})<-[r]-(o)
    RETURN DISTINCT type(r) AS relation_type, 'tail' AS direction
    """
    
    # 2. 执行查询
    head_relations = []
    tail_relations = []
    
    try:
        # 查询出度关系 (head)
        head_results = n4j_client.query_all(head_query, parameters={"entity_name": entity_name})
        head_relations = [record["relation_type"].lower() for record in head_results]
        
        # 查询入度关系 (tail)
        tail_results = n4j_client.query_all(tail_query, parameters={"entity_name": entity_name})
        tail_relations = [record["relation_type"].lower() for record in tail_results]
    except Exception as e:
        print(f"关系查询失败: {str(e)}")
    
    # 3. 过滤不必要的关系，暂不使用
    #if args.remove_unnecessary_rel:
    #    head_relations = [rel for rel in head_relations if not abandon_rels(rel)]
    #    tail_relations = [rel for rel in tail_relations if not abandon_rels(rel)]
    
    # 4. 根据前一轮关系过滤
    if pre_head:
        # 如果前一轮是 head，则过滤掉已经使用过的 tail 关系
        tail_relations = list(set(tail_relations) - set(pre_relations))
    else:
        # 如果前一轮是 tail，则过滤掉已经使用过的 head 关系
        head_relations = list(set(head_relations) - set(pre_relations))
    total_relations = list(head_relations|tail_relations)
    total_relations.sort()
    prompt = construct_relation_prune_prompt(question, entity_name, total_relations, args)
    result = run_llm(prompt, args.temperature_exploration, args.max_length, args.opeani_api_keys, args.LLM_type)
    flag, retrieve_relations_with_scores = clean_relations(result, entity_name, head_relations,args)
    if flag:
        return retrieve_relations_with_scores
    else:
        return []
    
def relation_search(entity_name, pre_relations, pre_head, question, args, n4j_client):
    """
    使用列表实现的关系搜索函数
    :param entity_name: 实体名称（作为ID）
    :param entity_name_dup: 实体名称（与entity_name相同）
    """
    # 定义查询
    head_query = """
    MATCH (e) 
    WHERE e.name = $entity_name OR e.title = $entity_name
    WITH e
    MATCH (e)-[r]->(o)
    RETURN DISTINCT type(r) AS relation_type, 'head' AS direction
    """
    
    tail_query = """
    MATCH (e) 
    WHERE e.name = $entity_name OR e.title = $entity_name
    WITH e
    MATCH (e)<-[r]-(o)
    RETURN DISTINCT type(r) AS relation_type, 'tail' AS direction
    """
    head_relations = []
    tail_relations = []
    try:
        # HEAD关系处理（兼容多种返回格式）
        head_results = n4j_client.query_all(head_query, parameters={"entity_name": entity_name})
        if isinstance(head_results, list):  # 列表类型结果
            for record in head_results:
                if isinstance(record, dict):  # 字典元素
                    rel_type = record.get("relation_type", "")
                else:  # 字符串元素
                    rel_type = str(record)
                if rel_type:
                    head_relations.append(rel_type.lower())
        
        # TAIL关系处理（同上）
        tail_results = n4j_client.query_all(tail_query, parameters={"entity_name": entity_name})
        if isinstance(tail_results, list):
            for record in tail_results:
                if isinstance(record, dict):
                    rel_type = record.get("relation_type", "")
                else:
                    rel_type = str(record)
                if rel_type:
                    tail_relations.append(rel_type.lower())
    except Exception as e:
        print(f"关系查询失败: {str(e)}")
    
    # 如果需要移除不必要的关系
    #if args.remove_unnecessary_rel:
    #    head_relations = [rel for rel in head_relations if not abandon_rels(rel)]
    #    tail_relations = [rel for rel in tail_relations if not abandon_rels(rel)]
    
    # 根据前一轮关系过滤
    if pre_head:
        tail_relations = set(tail_relations) - set(pre_relations)
    else:
        head_relations = set(head_relations) - set(pre_relations)

    head_relations = list(set(head_relations))
    h = [{"relation": s, 'head': True, 'entity_name': entity_name} for s in head_relations]  # 移除entity_name
    
    tail_relations = list(set(tail_relations))
    t = [{"relation": s, 'head': False, 'entity_name': entity_name} for s in tail_relations]  # 移除entity_name
    
    total_relations = h + t
    #print (total_relations)
    return total_relations


def entity_search(entity_name, relation, n4j_client, head):
    """在 Neo4j 中搜索与实体相关的关系和目标实体"""
    # 使用更灵活的查询
    if head:
        cql = """
        MATCH (source) 
        WHERE source.name = $entity_name OR source.title = $entity_name
        WITH source
        MATCH (source)-[r]->(target)
        WHERE type(r) = $relation_upper OR type(r) = $relation_lower
        RETURN COALESCE(
            target.name, 
            target.title, 
            target.content
        ) AS name
        """
    else:
        cql = """
        MATCH (target) 
        WHERE target.name = $entity_name OR target.title = $entity_name
        WITH target
        MATCH (source)-[r]->(target)
        WHERE type(r) = $relation_upper OR type(r) = $relation_lower
        RETURN COALESCE(
            source.name, 
            source.title, 
            source.content
        ) AS name
        """

    # 准备参数
    params = {
        "entity_name": entity_name,
        "relation_upper": relation.upper(),
        "relation_lower": relation.lower()
    }
    
    # 执行查询
    candidate_list = []
    try:
        results = n4j_client.query_all(cql, parameters=params)
        
        # 处理结果
        if isinstance(results, list):
            for record in results:
                if isinstance(record, dict):
                    name = record.get("name", "")
                else:
                    name = str(record)
                
                if name and len(name) > 1:
                    candidate_list.append({
                        'name': name,
                        'id': name
                    })
                    print(f"relation 对应的候选实体: {name}")
    except Exception as e:
        print(f"实体搜索失败: {str(e)}")
    
    # 如果结果太多，随机采样
    if len(candidate_list) >= 50:
        candidate_list = random.sample(candidate_list, 50)
    
    return candidate_list

def update_history_find_entity(entity_candidates_find, relation, total_candidates):
    """
    更新历史找到的实体列表
    :param entity_candidates_find: 当前找到的实体候选列表
    :param relation: 当前关系信息
    :param total_candidates: 总候选实体列表
    :return: 更新后的总候选实体列表
    """
    for entity_candidate in entity_candidates_find:
        candidate = {
            'relation': relation['relation'],  # 关系类型
            'topic_entities': relation['entity_name'],  # 源实体名称
            'id': entity_candidate['id'],  # 目标实体ID（名称）
            'name': entity_candidate['name'],  # 目标实体名称
            'related_paragraphs': entity_candidate.get('related_paragraphs', []),  # 相关段落
        }
        
        # 添加方向信息（如果存在）
        if 'head' in relation:
            candidate['head'] = relation['head']
        
        # 添加前置路径信息（如果存在）
        if 'pre_path' in entity_candidate:
            candidate["pre_path"] = entity_candidate['pre_path']
        
        # 添加到总候选列表
        total_candidates.append(candidate)
    
    return total_candidates

def para_rank_topk(question, Indepth_total_candidates, args, emb_model, k=10):
    """对段落进行排序并选择 top-k 相关实体"""
    # 1. 收集所有段落并计算相关性分数
    all_paragraphs = []
    for candidate in Indepth_total_candidates:
        all_paragraphs.extend(candidate.get('related_paragraphs', []))
    
    # 计算每个段落的相关性分数
    paragraph_scores = s2p_relevance_scores(all_paragraphs, question, args, emb_model)
    
    # 2. 创建 top-k 段落堆
    top_paragraphs_heap = []
    score_index = 0
    counter = 0  # 用于解决比较问题的计数器
    
    for candidate in Indepth_total_candidates:
        for paragraph in candidate.get('related_paragraphs', []):
            # 获取当前段落的分数
            score = paragraph_scores[score_index]
            score_index += 1
            
            # 创建段落信息对象
            paragraph_info = {
                'text': paragraph,
                'score': score,
                'entity_name': candidate.get('name', ''),
                'entity_id': candidate.get('id', ''),
                'relation': candidate.get('relation', ''),
                'topic_entities': candidate.get('topic_entities', ''),
                'head': candidate.get('head', False)
            }
            
            # 添加到堆中 - 使用元组 (score, counter, paragraph_info)
            heapq.heappush(top_paragraphs_heap, (score, counter, paragraph_info))
            counter += 1  # 递增计数器
            
            # 保持堆大小为 k
            if len(top_paragraphs_heap) > k:
                heapq.heappop(top_paragraphs_heap)
    
    # 3. 提取 top-k 段落（按分数降序）
    top_k_paragraphs = []
    while top_paragraphs_heap:
        score, cnt, paragraph_info = heapq.heappop(top_paragraphs_heap)
        top_k_paragraphs.append(paragraph_info)
    top_k_paragraphs.reverse()  # 从高到低排序
    
    # 4. 计算实体加权分数
    entities_with_score = {}
    alpha = 0.8
    
    for rank, paragraph_info in enumerate(top_k_paragraphs, start=1):
        entity_name = paragraph_info['entity_name']
        score = float(paragraph_info['score'])
        weight = math.exp(-alpha * rank)
        
        if entity_name in entities_with_score:
            entities_with_score[entity_name] += score * weight
        else:
            entities_with_score[entity_name] = score * weight
    
    # 5. 选择 top 实体
    sorted_entities = sorted(entities_with_score.items(), key=lambda x: x[1], reverse=True)
    sorted_entity_list = []
    
    for i in range(min(args.width, len(sorted_entities))):
        entity_name, entity_score = sorted_entities[i]
        
        # 查找实体的完整信息
        entity_info = None
        for candidate in Indepth_total_candidates:
            if candidate.get('name') == entity_name:
                entity_info = candidate.copy()
                break
        
        if not entity_info:
            continue
        
        # 收集所有相关句子
        all_sentences = []
        for paragraph_info in top_k_paragraphs:
            if paragraph_info['entity_name'] == entity_name:
                # 分割段落为句子
                sentences = split_sentences_windows(paragraph_info['text'], *args.sliding_window)
                all_sentences.extend(sentences)
        
        # 创建带分数的句子列表
        sents_dict = [{'text': s, 'score': 0} for s in all_sentences]
        
        # 更新实体信息
        entity_info.update({
            'entity_score': entity_score,
            'sentences': sents_dict
        })
        
        sorted_entity_list.append(entity_info)
    
    # 6. 提取实体信息
    entities_id = [d['id'] for d in sorted_entity_list]
    relations = [d['relation'] for d in sorted_entity_list]
    entities_name = [d['name'] for d in sorted_entity_list]
    topics = [d['topic_entities'] for d in sorted_entity_list]
    heads = [d.get('head', False) for d in sorted_entity_list]
    
    if not sorted_entity_list:
        return False, [], [], [], [], [], Indepth_total_candidates
    
    # 7. 创建实体链
    cluster_chain_of_entities = [
        (topics[i], relations[i], entities_name[i]) 
        for i in range(len(entities_name))
    ]
    
    return True, cluster_chain_of_entities, entities_id, relations, heads, sorted_entity_list, Indepth_total_candidates
def contains_yes_regex(text):
    """检查文本前100个单词中是否包含 '是'"""
    if not isinstance(text, str):
        return False
    
    # 只检查前1000个字符以提高效率
    text_to_check = text[:1000].lower()
    
    # 使用更高效的方式检查
    return '是' in text_to_check.split()[:100]

def reasoning(question, Indepth_total_candidates, Total_Related_Senteces, cluster_chain_of_entities, args, clue):
    """使用 LLM 进行推理"""
    def num_tokens_from_string(string: str) -> int:
        """计算字符串的 token 数量"""
        import tiktoken
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding.encode(string))
    
    # 构建实体链提示
    chain_prompt = '(' + ')\n('.join([
        ', '.join([str(x) for x in chain]) 
        for chain in cluster_chain_of_entities
    ]) + ')'
    
    # 根据数据集类型构建提示
    if 'fever' in args.dataset or 'creak' in args.dataset:
        check_prompt = '### Claim:' + question
        if "fever" in args.dataset:
            system_prompt = prompt_reasoning_fever_3shot_2
            if args.clue_query:
                chain_prompt += '\n' + 'clue:' + clue + '\n'
                system_prompt = prompt_reasoning_fever_query_change_3shot_2
        else:
            system_prompt = vanilla_prompt_fact_check_3shot
            if args.clue_query:
                chain_prompt += '\n' + 'clue:' + clue + '\n'
                system_prompt = prompt_reasoning_creak_query_change_3shot
    else:
        check_prompt = '### Question:' + question
        system_prompt = prompt_reasoning_qa_2shot
        if args.clue_query:
            chain_prompt += '\n' + 'clue:' + clue + '\n'
            system_prompt = prompt_reasoning_qa_query_change_2shot
    
    # 处理相关句子
    sorted_sentences = Total_Related_Senteces[:args.num_sents_for_reasoning]
    texts = [sentence['text'] for sentence in sorted_sentences]
    
    # 计算 token 数量并构建提示
    base_tokens = num_tokens_from_string(
        system_prompt + "\nKnowledge Triplets:\n" + chain_prompt + 
        '\nRetrieved sentences:\n' + '\nAnswer:'
    )
    
    related_sentences_prompt = ''
    for text in texts:
        text_tokens = num_tokens_from_string(text) + 1
        if base_tokens + text_tokens < 30000:
            related_sentences_prompt += '\n' + text
            base_tokens += text_tokens
        else:
            break
    
    # 构建最终提示
    check_prompt += (
        "\n### Knowledge Triplets:\n" + chain_prompt +
        '\n### Retrieved References:\n' + related_sentences_prompt + 
        '\n### Answer:'
    )
    final_prompt = system_prompt + check_prompt
    
    # 运行 LLM
    response = run_llm(
        final_prompt, 
        args.temperature_reasoning, 
        args.max_length, 
        args.opeani_api_keys, 
        args.LLM_type
    )
    
    print('-----------reasoning result-----------')
    #print("prompt:111111111111111111111111111111111111111111111111",final_prompt)
    print(response)
    
    # 提取答案并判断是否停止
    result = extract_answer(response)
    if if_true(result) or contains_yes_regex(response):
        return True, response, final_prompt, clue
    else:
        clue = extract_clue(response)
        return False, response, final_prompt, clue

def if_finish_list(lst):
    """检查列表中是否所有元素都是 [FINISH_ID]"""
    if all(elem == "[FINISH_ID]" for elem in lst):
        return True, []
    else:
        new_lst = [elem for elem in lst if elem != "[FINISH_ID]"]
        return False, new_lst