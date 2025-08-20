from pathlib import Path
from neo4j_client import *
from utils import *
from search import *
import torch
from database_func import *
from dotenv import load_dotenv

load_dotenv()
class Args:
    def __init__(self):
        self.dataset = "custom"
        self.samples = 2000
        self.start = 0
        self.max_length = None
        self.temperature_exploration = 0.0
        self.temperature_reasoning = 0.0
        self.width = 3
        self.depth = 5
        self.remove_unnecessary_rel = True
        self.LLM_type = 'qwen-max'  # 'llama3'
        self.LLM_type_rp = 'qwen-max'  # 'llama3'
        self.opeani_api_keys = os.getenv("OPENAI_API_KEY")
        self.server_addrs = os.getenv("NEO4J_SERVER_ADDRS").split(';')
        self.embedding_model_name = 'minilm'
        self.relation_prune = True
        self.relation_prune_combination = True
        self.num_sents_for_reasoning = 10
        self.topic_prune = True
        self.gpt_only = False
        self.self_consistency = 0
        self.self_consistency_threshold = 0.8
        self.clue_query = True
        self.sliding_window = (1, 1)
        self.output = f"{self.dataset}_self_consistency"

args = Args()

start = args.start
datas, question_string = prepare_dataset(args.dataset)

print(f"CUDA 可用: {torch.cuda.is_available()}")
print(f"检测到 GPU 数量: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"当前 GPU: {torch.cuda.current_device()}")

n4j_client = Neo4jQueryClient(
    args.server_addrs, 
    user=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
)


MODEL_ROOT = "./models"  

if args.embedding_model_name == "bge-bi":
    from FlagEmbedding import FlagModel
    print('Loading bge embedding model from local...')
    model_path = os.path.join(MODEL_ROOT, "bge/bge-large-en-v1.5")
    emb_model = FlagModel(model_path, use_fp16=False)
    
elif args.embedding_model_name == "minilm":
    from sentence_transformers import SentenceTransformer
    model_path = os.path.join(MODEL_ROOT, "minilm/paraphrase-multilingual-MiniLM-L12-v2")
    emb_model = SentenceTransformer(model_path)
    
elif args.embedding_model_name == "bm25":
    print('Initializing BM25...')
    emb_model = compute_bm25_similarity  
    
elif args.embedding_model_name == 'bge-ce':
    from FlagEmbedding import FlagReranker
    print("Loading bge reranker from local...")
    model_path = os.path.join(MODEL_ROOT, "bge/bge-reranker-large")
    emb_model = FlagReranker(model_path, use_fp16=False)
    
elif args.embedding_model_name == 'colbert':
    from FlagEmbedding import BGEM3FlagModel
    print("Loading Colbert from local...")
    model_path = os.path.join(MODEL_ROOT, "colbert/bge-m3")
    emb_model = BGEM3FlagModel(model_path, use_fp16=True)

samples_length = args.samples

print("Start Running ToG on %s dataset." % args.dataset)

print('Dataset length: ' + str(len(datas)))

print('Test samples length: ' + str(samples_length))




def main_n4j_new(original_question, topic_entity, ground_truth, data_point):
    clue = ''
    question = original_question
    print('\n')
    print('Question   ' + question)
    print('topic_entity   ' + str(','.join(topic_entity)))
    print('\n')
    cluster_chain_of_entities = []
    search_entity_list = []
    Total_Related_Senteces = []

    if args.self_consistency:#自一致性检查
        if data_point["cot_sc_score"] >= args.self_consistency_threshold:
            return data_point["cot_sc_response"], search_entity_list, [], [], 'gpt self-consistency', ''

    if len(topic_entity) == 0 or args.gpt_only:#跳过知识检索直接使用llm回答
        answer = generate_only_with_gpt(question, args)
        endmode = 'generate_without_explored_paths'
        remark = 'no_topic_entity'
        print(remark)
        return answer, search_entity_list, [], [], endmode, remark
    
    if args.topic_prune and len(topic_entity) > 2:#entity剪枝
        print('--------------- topic entity prune ---------------')
        topic_entity = topic_e_prune(question, topic_entity, args)

        if len(topic_entity) == 0:#没有可用entity，直接使用llm回答
            answer = generate_only_with_gpt(question, args)
            endmode = 'generate_without_explored_paths.'
            remark = 'no_topic_entity_tp'
            print(remark)
            return answer, search_entity_list, [], [], endmode, remark
    else:
        print("No topic prune.")


    print('\n---------------collecting topic_entity docs---------------')
    for entity_name in topic_entity:
        related_passage = get_original_text(n4j_client, {'name': entity_name})
        if related_passage and related_passage != "Not Found!":
            paragraphs = [p for p in related_passage.split('\n') if p.strip()]
            for para in paragraphs:
                sentences = split_sentences_windows(para, *args.sliding_window)
                Total_Related_Senteces.extend(sentences)
        

    if args.depth == 0:
        references = ''
        if len(Total_Related_Senteces) > 0:
            references += "# References \n"
            for idx, s in enumerate(Total_Related_Senteces[:args.num_sents_for_reasoning]):
                references += s.strip() + '\n' 
        if 'fever' in args.dataset or 'creak' in args.dataset:
            check_prompt = '### Claim:' + question
            if "fever" in args.dataset:
                system_prompt = prompt_reasoning_fever_3shot_2
            else:
                system_prompt = prompt_reasoning_creak_3shot
        else:
            check_prompt = '### Question:' + question
            system_prompt = vanilla_prompt_reasoning_qa_2shot
        final_prompt = system_prompt + '\n' + check_prompt + '\n' + references + '\n'
        answer = run_llm(final_prompt, 0, 512, args.opeani_api_keys)
        return answer, [], [], [], '', ''

    pre_relations = [''] * len(topic_entity)
    pre_heads = [-1] * len(topic_entity)

    for depth in range(1, args.depth + 1):
        print('\n-----------------------depth: ' + str(depth) + '-----------------------')
        current_entity_relations_list = []
        all_entity_relations = {}

        # 遍历每个实体
        for index, entity_name in enumerate(topic_entity):
            if entity_name != "[FINISH_ID]":
                if args.relation_prune:
                    if args.relation_prune_combination:
                        # 组合剪枝模式 - 直接使用实体名称作为标识
                        retrieve_relations = relation_search(
                            entity_name,  # 直接使用实体名称检索
                            pre_relations[index],
                            pre_heads[index],
                            question,
                            args,
                            n4j_client
                        )
                        # 使用实体名称作为键存储关系
                        if entity_name in all_entity_relations:
                            all_entity_relations[entity_name].extend(retrieve_relations)
                        else:
                            all_entity_relations[entity_name] = retrieve_relations
                    else:
                        # 非组合剪枝模式
                        retrieve_relations_with_scores = relation_search_prune(
                            entity_name,  # 使用实体名称检索
                            entity_name,  # 实体名称
                            pre_relations[index],
                            pre_heads[index],
                            question,
                            args,
                            n4j_client
                        )
                        # 添加实体信息
                        for relation in retrieve_relations_with_scores:
                            relation['entity_name'] = entity_name
                        current_entity_relations_list.extend(retrieve_relations_with_scores)
                else:
                    # 无剪枝模式
                    retrieve_relations = relation_search(
                        entity_name,  # 使用实体名称检索
                        entity_name,  # 实体名称
                        pre_relations[index],
                        pre_heads[index],
                        question,
                        args,
                        n4j_client
                    )
                    # 添加实体信息
                    for relation in retrieve_relations:
                        relation['entity_name'] = entity_name
                    current_entity_relations_list.extend(retrieve_relations)
        
        # 组合剪枝处理（在所有实体处理完成后）
        if args.relation_prune and args.relation_prune_combination:
            #relation_prune_all(all_entity_relations, question, args)
            # 组合剪枝模式下，将所有实体关系平铺到当前列表
            for entity_name, relations in all_entity_relations.items():
                for rel in relations:
                    rel['entity_name'] = entity_name  # 确保每个关系都有实体名称
                current_entity_relations_list.extend(relations)

        # 打印结果
        print('\n---------------Find relation for: {}.---------------'.format(','.join(topic_entity)))
        print('---------------total ' + str(len(current_entity_relations_list)) + ' rels')
        for rel in current_entity_relations_list:
            print('entity name:', rel['entity_name'], ' relation name:', rel['relation'])
        print('\n')
        
        if depth == 1 and len(current_entity_relations_list) == 0:
            answer = generate_only_with_gpt(question, args)
            remark = 'WiKi Error: cant find relation of first topic_entity. Depth 1 '
            print(remark, ": ", question)
            end_mode = 'generate_only_with_gpt'
            return answer, search_entity_list, Total_Related_Senteces, [], end_mode, remark
        if depth == 1 and len(current_entity_relations_list) == 0:
            answer = generate_only_with_gpt(question, args)
            remark = 'WiKi Error: cant find relation of first topic_entity. Depth 1 '
            print(remark, ": ", question)
            end_mode = 'generate_only_with_gpt'

            return answer, search_entity_list, Total_Related_Senteces, [], end_mode, remark

        Indepth_total_candidates = []
        each_relation_right_entityList = []
        for relation in current_entity_relations_list:
            print('\n-------------Searching ' + str(relation['entity_name']) + ' relation: ' + str(
                relation['relation']))
    
            # 根据方向调用 entity_search
            if relation['head']:
                entity_candidates = entity_search(
                    relation['entity_name'], 
                    relation['relation'], 
                    n4j_client,  # 传入 Neo4j 客户端
                    True  # head 方向
                )
            else:
                entity_candidates = entity_search(
                    relation['entity_name'], 
                    relation['relation'], 
                    n4j_client,  # 传入 Neo4j 客户端
                    False  # tail 方向
                )
    
            # 统一处理所有方向的候选实体
            if len(entity_candidates) == 0:
                print("未找到候选实体")
                continue
    
            #print('\n---------------Collected entity_candidates---------------')
            #print(entity_candidates)
    
            entity_candidates = [candidate for candidate in entity_candidates if len(candidate['name']) >= 2]
            print('---------------Collecting entity_candidates docs---------------')
            for candidate in entity_candidates:
                if candidate['id'] != '[FINISH_ID]':
                    original_text = get_original_text(n4j_client, candidate)
                    if original_text and original_text != "Not Found!":                        # 将文本分割为段落
                        paragraphs = [p for p in original_text.split('\n') if p.strip()]
                        candidate['related_paragraphs'] = paragraphs
                    else:
                     candidate['related_paragraphs'] = []
                else:
                    candidate['related_paragraphs'] = []

            # 过滤掉没有相关段落的候选实体
            entity_candidates = [candidate for candidate in entity_candidates if
                                 bool(candidate.get('related_paragraphs'))]
            
            # 更新历史找到的实体
            Indepth_total_candidates = update_history_find_entity(entity_candidates, relation, Indepth_total_candidates)
            
                # 添加到关系-实体列表
            each_relation_right_entityList.append({
                'current_relation': relation, 
                'right_entity': entity_candidates
            })

            # 将当前深度的搜索结果添加到总列表
        search_entity_list.append({
            'depth': depth, 
            'current_entity_relations_list': current_entity_relations_list,
            'each_relation_right_entityList': each_relation_right_entityList})

        if len(Indepth_total_candidates) == 0:
            if depth:
                answer = generate_only_with_gpt(question, args)
                remark = 'no entity find in depth{}'.format(depth)
                end_mode = 'generate_only_with_gpt'
                #print(remark)
                return answer, search_entity_list, Total_Related_Senteces, [], end_mode, remark

        #print(Indepth_total_candidates)
        flag, chain_of_entities, entities_id, pre_relations, pre_heads, sorted_entity_list, Indepth_total_candidates = para_rank_topk(
                question, Indepth_total_candidates, args, emb_model)

        cluster_chain_of_entities.append(chain_of_entities)

        if flag:
            for entity in sorted_entity_list:
                s = entity.get('sentences', [])
                s = [sentence if isinstance(sentence, dict) else {'text': str(sentence)}
                     for sentence in s]
                Total_Related_Senteces.extend(s)
            
            unique_sentences = {}
            for sentence in Total_Related_Senteces:
                if not isinstance(sentence, dict):
                    sentence = {'text': str(sentence)}
                
                text = sentence.get('text', '')
                if text:
                    unique_sentences[text] = sentence
            
            Total_Related_Senteces = list(unique_sentences.values())
            
            # 计算句子相关性分数
            sents_text = [s.get('text', '') for s in Total_Related_Senteces]
            scores = s2p_relevance_scores(sents_text, question, args, emb_model)
            print(sents_text,scores)

            Total_Related_Senteces = scores_rank(scores, sents_text)

            stop, answer, kg_prompt,clue = reasoning(
                original_question, 
                Indepth_total_candidates, 
                Total_Related_Senteces,
                cluster_chain_of_entities, 
                args, 
                clue
            )
            
            if stop:
                print(f"\n-----------------------Find answer. ToG stopped at depth {depth}.")
                end_mode = 'reasoning stop'
                remark = f"Find answer. ToG stopped at depth {depth}."
                return answer, search_entity_list, Total_Related_Senteces, cluster_chain_of_entities, end_mode, remark
            else:
                print(f"\n-----------------------depth {depth} still not find the answer.")
                flag_finish, entities_id = if_finish_list(entities_id)

                if flag_finish:
                    answer = generate_only_with_gpt(question, args)
                    remark = f"After entity_find_prune, all entities_id == [FINISH_ID]. No new knowledge added during search depth {depth}, stop searching."
                    end_mode = 'generate_only_with_gpt'
                    print(remark)
                    return answer, search_entity_list, Total_Related_Senteces, [], end_mode, remark
                else:
                    # 使用 Neo4j 获取实体名称
                    topic_entity = {}
                    for entity_id in entities_id:
                        #entity_name = get_entity_name_from_neo4j(n4j_client, entity_id)
                        entity_name = entity_id
                        topic_entity[entity_id] = entity_name
                    continue
        else:
            remark = f'Last situation topic entity rank list in empty in depth {depth}, generate_only_with llm.'
            end_mode = 'generate_only_with_gpt'
            print(remark)
            
            if 'fever' in args.dataset:
                answer = 'The answer is {NOT ENOUGH INFO}.'
            else:
                answer = generate_only_with_gpt(question, args)
            return answer, search_entity_list, Total_Related_Senteces, [], end_mode, remark
    answer = generate_only_with_gpt(question, args)
    remark = 'Last situation.Not into depth. whether it trigger'
    end_mode = 'generate_only_with_gpt'
    print(remark)
    return answer, search_entity_list, Total_Related_Senteces, [], end_mode, remark




length = min(samples_length, len(datas))

for i in range(start, length):
    data = datas[i]
    query = data[question_string]
    if args.self_consistency:
        data_point = self_consistency(query, data, i, args)
    else:
        data_point = []
    if 'qid_topic_entity' in data:
        topic_entity = data['qid_topic_entity']
    elif 'entities' in data:
        topic_entity = data['entities']
    else:
        print(f"问题: '{query}'")
        topic_entity = get_entities_from_neo4j(n4j_client,query, emb_model)
    if 'answer' in data:
        ground_truth = data["answer"]
    elif 'answers' in data:
        ground_truth = data["answers"]
    elif 'fever' in args.dataset:
        ground_truth = data['label']
    else:
        ground_truth = ''

    answer, search_entity_list, Total_Related_Senteces, cluster_chain_of_entities, end_mode, remark = main_n4j_new(
        query, topic_entity, ground_truth, data_point)
    
    def extract_final_subtasks(answer):
        start_index = answer.find("[")
        end_index = answer.find("]")
        return answer[start_index+1: end_index]
    
    print('FINAL ANSWER:')
    print(extract_final_subtasks(answer))
    save_2_jsonl_simplier(query, ground_truth, answer, search_entity_list, Total_Related_Senteces,
                          cluster_chain_of_entities, args.dataset, end_mode, remark, args)
