extract_relation_prompt = """Please retrieve %s relations (separated by semicolon) that contribute to the question and rate their contribution on a scale from 0 to 1 (the sum of the scores of %s relations is 1).
Q: Name the president of the country whose main spoken language was Brahui in 1980?
Topic Entity: Brahui Language
Relations: language.human_language.main_country; language.human_language.language_family; language.human_language.iso_639_3_code; base.rosetta.languoid.parent; language.human_language.writing_system; base.rosetta.languoid.languoid_class; language.human_language.countries_spoken_in; kg.object_profile.prominent_type; base.rosetta.languoid.document; base.ontologies.ontology_instance.equivalent_instances; base.rosetta.languoid.local_name; language.human_language.region
A: 1. {language.human_language.main_country (Score: 0.4))}: This relation is highly relevant as it directly relates to the country whose president is being asked for, and the main country where Brahui language is spoken in 1980.
2. {language.human_language.countries_spoken_in (Score: 0.3)}: This relation is also relevant as it provides information on the countries where Brahui language is spoken, which could help narrow down the search for the president.
3. {base.rosetta.languoid.parent (Score: 0.2)}: This relation is less relevant but still provides some context on the language family to which Brahui belongs, which could be useful in understanding the linguistic and cultural background of the country in question.

Q: """


score_entity_candidates_prompt = """Please score the entities' contribution to the question on a scale from 0 to 1 (the sum of the scores of all entities is 1).
Q: The movie featured Miley Cyrus and was produced by Tobin Armbrust?
Relation: film.producer.film
Entites: The Resident; So Undercover; Let Me In; Begin Again; The Quiet Ones; A Walk Among the Tombstones
Score: 0.0, 1.0, 0.0, 0.0, 0.0, 0.0
The movie that matches the given criteria is "So Undercover" with Miley Cyrus and produced by Tobin Armbrust. Therefore, the score for "So Undercover" would be 1, and the scores for all other entities would be 0.

Q: {}
Relation: {}
Entites: """

answer_prompt = """Given a question and the associated retrieved knowledge graph triplets (entity, relation, entity), you are asked to answer the question with these triplets and your knowledge.
Q: Find the person who said \"Taste cannot be controlled by law\", what did this person die from?
Knowledge Triplets: Taste cannot be controlled by law., media_common.quotation.author, Thomas Jefferson
A: Based on the given knowledge triplets, it's not sufficient to answer the entire question. The triplets only provide information about the person who said "Taste cannot be controlled by law," which is Thomas Jefferson. To answer the second part of the question, it's necessary to have additional knowledge about where Thomas Jefferson's dead.

Q: The artist nominated for The Long Winter lived where?
Knowledge Triplets: The Long Winter, book.written_work.author, Laura Ingalls Wilder
Laura Ingalls Wilder, people.person.places_lived, Unknown-Entity
Unknown-Entity, people.place_lived.location, De Smet
A: Based on the given knowledge triplets, the author of The Long Winter, Laura Ingalls Wilder, lived in De Smet. Therefore, the answer to the question is {De Smet}.

Q: Who is the coach of the team owned by Steve Bisciotti?
Knowledge Triplets: Steve Bisciotti, sports.professional_sports_team.owner_s, Baltimore Ravens
Steve Bisciotti, sports.sports_team_owner.teams_owned, Baltimore Ravens
Steve Bisciotti, organization.organization_founder.organizations_founded, Allegis Group
A: Based on the given knowledge triplets, the coach of the team owned by Steve Bisciotti is not explicitly mentioned. However, it can be inferred that the team owned by Steve Bisciotti is the Baltimore Ravens, a professional sports team. Therefore, additional knowledge about the current coach of the Baltimore Ravens can be used to answer the question.

Q: Rift Valley Province is located in a nation that uses which form of currency?
Knowledge Triplets: Rift Valley Province, location.administrative_division.country, Kenya
Rift Valley Province, location.location.geolocation, UnName_Entity
Rift Valley Province, location.mailing_address.state_province_region, UnName_Entity
Kenya, location.country.currency_used, Kenyan shilling
A: Based on the given knowledge triplets, Rift Valley Province is located in Kenya, which uses the Kenyan shilling as its currency. Therefore, the answer to the question is {Kenyan shilling}.

Q: The country with the National Anthem of Bolivia borders which nations?
Knowledge Triplets: National Anthem of Bolivia, government.national_anthem_of_a_country.anthem, UnName_Entity
National Anthem of Bolivia, music.composition.composer, Leopoldo Benedetto Vincenti
National Anthem of Bolivia, music.composition.lyricist, José Ignacio de Sanjinés
UnName_Entity, government.national_anthem_of_a_country.country, Bolivia
Bolivia, location.country.national_anthem, UnName_Entity
A: Based on the given knowledge triplets, we can infer that the National Anthem of Bolivia is the anthem of Bolivia. Therefore, the country with the National Anthem of Bolivia is Bolivia itself. However, the given knowledge triplets do not provide information about which nations border Bolivia. To answer this question, we need additional knowledge about the geography of Bolivia and its neighboring countries.

Q: {}
"""

prompt_evaluate="""Given a question and the associated retrieved knowledge graph triplets (entity, relation, entity), you are asked to answer whether it's sufficient for you to answer the question with these triplets and your knowledge (Yes or No).
Q: Find the person who said \"Taste cannot be controlled by law\", what did this person die from?
Knowledge Triplets: Taste cannot be controlled by law., media_common.quotation.author, Thomas Jefferson
A: {No}. Based on the given knowledge triplets, it's not sufficient to answer the entire question. The triplets only provide information about the person who said "Taste cannot be controlled by law," which is Thomas Jefferson. To answer the second part of the question, it's necessary to have additional knowledge about where Thomas Jefferson's dead.

Q: The artist nominated for The Long Winter lived where?
Knowledge Triplets: The Long Winter, book.written_work.author, Laura Ingalls Wilder
Laura Ingalls Wilder, people.person.places_lived, Unknown-Entity
Unknown-Entity, people.place_lived.location, De Smet
A: {Yes}. Based on the given knowledge triplets, the author of The Long Winter, Laura Ingalls Wilder, lived in De Smet. Therefore, the answer to the question is {De Smet}.

Q: Who is the coach of the team owned by Steve Bisciotti?
Knowledge Triplets: Steve Bisciotti, sports.professional_sports_team.owner_s, Baltimore Ravens
Steve Bisciotti, sports.sports_team_owner.teams_owned, Baltimore Ravens
Steve Bisciotti, organization.organization_founder.organizations_founded, Allegis Group
A: {No}. Based on the given knowledge triplets, the coach of the team owned by Steve Bisciotti is not explicitly mentioned. However, it can be inferred that the team owned by Steve Bisciotti is the Baltimore Ravens, a professional sports team. Therefore, additional knowledge about the current coach of the Baltimore Ravens can be used to answer the question.

Q: Rift Valley Province is located in a nation that uses which form of currency?
Knowledge Triplets: Rift Valley Province, location.administrative_division.country, Kenya
Rift Valley Province, location.location.geolocation, UnName_Entity
Rift Valley Province, location.mailing_address.state_province_region, UnName_Entity
Kenya, location.country.currency_used, Kenyan shilling
A: {Yes}. Based on the given knowledge triplets, Rift Valley Province is located in Kenya, which uses the Kenyan shilling as its currency. Therefore, the answer to the question is {Kenyan shilling}.

Q: The country with the National Anthem of Bolivia borders which nations?
Knowledge Triplets: National Anthem of Bolivia, government.national_anthem_of_a_country.anthem, UnName_Entity
National Anthem of Bolivia, music.composition.composer, Leopoldo Benedetto Vincenti
National Anthem of Bolivia, music.composition.lyricist, José Ignacio de Sanjinés
UnName_Entity, government.national_anthem_of_a_country.country, Bolivia
Bolivia, location.country.national_anthem, UnName_Entity
A: {No}. Based on the given knowledge triplets, we can infer that the National Anthem of Bolivia is the anthem of Bolivia. Therefore, the country with the National Anthem of Bolivia is Bolivia itself. However, the given knowledge triplets do not provide information about which nations border Bolivia. To answer this question, we need additional knowledge about the geography of Bolivia and its neighboring countries.

"""

generate_directly = """Q: What state is home to the university that is represented in sports by George Washington Colonials men's basketball?
A: First, the education institution has a sports team named George Washington Colonials men's basketball in is George Washington University , Second, George Washington University is in Washington D.C. The answer is {Washington, D.C.}.

Q: Who lists Pramatha Chaudhuri as an influence and wrote Jana Gana Mana?
A: First, Bharoto Bhagyo Bidhata wrote Jana Gana Mana. Second, Bharoto Bhagyo Bidhata lists Pramatha Chaudhuri as an influence. The answer is {Bharoto Bhagyo Bidhata}.

Q: Who was the artist nominated for an award for You Drive Me Crazy?
A: First, the artist nominated for an award for You Drive Me Crazy is Britney Spears. The answer is {Jason Allen Alexander}.

Q: What person born in Siegen influenced the work of Vincent Van Gogh?
A: First, Peter Paul Rubens, Claude Monet and etc. influenced the work of Vincent Van Gogh. Second, Peter Paul Rubens born in Siegen. The answer is {Peter Paul Rubens}.

Q: What is the country close to Russia where Mikheil Saakashvii holds a government position?
A: First, China, Norway, Finland, Estonia and Georgia is close to Russia. Second, Mikheil Saakashvii holds a government position at Georgia. The answer is {Georgia}.

Q: What drug did the actor who portrayed the character Urethane Wheels Guy overdosed on?
A: First, Mitchell Lee Hedberg portrayed character Urethane Wheels Guy. Second, Mitchell Lee Hedberg overdose Heroin. The answer is {Heroin}."""

score_entity_candidates_prompt_wiki0 = """Please score the entities' contribution to the question on a scale from 0 to 1 (the sum of the scores of all entities is 1).
Q: Staten Island Summer, starred what actress who was a cast member of "Saturday Night Live"?
Relation: cast member
Entites: Ashley Greene; Bobby Moynihan; Camille Saviola; Cecily Strong; Colin Jost; Fred Armisen; Gina Gershon; Graham Phillips; Hassan Johnson; Jackson Nicoll; Jim Gaffigan; John DeLuca; Kate Walsh; Mary Birdsong
Score: 0.0, 0.0, 0.0, 0.4, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4, 0.0
To score the entities\' contribution to the question, we need to determine which entities are relevant to the question and have a higher likelihood of being the correct answer.
In this case, we are looking for an actress who was a cast member of "Saturday Night Live" and starred in the movie "Staten Island Summer." Based on this information, we can eliminate entities that are not actresses or were not cast members of "Saturday Night Live."
The relevant entities that meet these criteria are:\n- Ashley Greene\n- Cecily Strong\n- Fred Armisen\n- Gina Gershon\n- Kate Walsh\n\nTo distribute the scores, we can assign a higher score to entities that are more likely to be the correct answer. In this case, the most likely answer would be an actress who was a cast member of "Saturday Night Live" around the time the movie was released.
Based on this reasoning, the scores could be assigned as follows:\n- Ashley Greene: 0\n- Cecily Strong: 0.4\n- Fred Armisen: 0.2\n- Gina Gershon: 0\n- Kate Walsh: 0.4

Q: {}
Relation: {}
Entites: """

find_entity_candidates_prompt_wiki = """Please identify the two Entites Most relevant to the question in the following Entites, to fill the Triplet (Entity-Relationship-Entity). Please refer to Related References for entities. You must choose two entities in the Entites list, and enclose each in curly brackets like {{xxx}},{{xxx}} in the answer.
Question: Staten Island Summer, starred what actress who was a cast member of "Saturday Night Live"?
Triplet:({{Staten Island Summer}}--{{cast member}}--?)
Entites:
{{Ashley Greene}},{{Bobby Moynihan}},{{Camille Saviola}},{{Cecily Strong}},{{Mary Birdsong}}
Related References: 
{{Entity: Ashley Greene}}:{{Reference: is an American actress and model, best known for her role as Alice Cullen in the "Twilight" film series.}}; 
{{Entity: Bobby Moynihan}}:{{Reference: is an American actor and comedian who was a cast member on "Saturday Night Live" from 2008 to 2017. While I couldn't find a direct connection between Bobby Moynihan and the film "Staten Island Summer" }}; 
{{Entity: Camille Saviola}}:{{Reference: is an American actress known for her work in both film and theater. However, there doesn't appear to be a direct connection between Camille Saviola and the question about "Staten Island Summer" and "Saturday Night Live."}}; 
{{Entity: Cecily Strong}}:{{Reference: is an American actress and comedian who is best known as a cast member on "Saturday Night Live." She has been a part of the show since 2012 and has gained recognition for her comedic performances. }}; 
{{Entity: Kate Walsh}}:{{Reference: is an American actress best known for her role as Dr. Addison Montgomery in the television series "Grey's Anatomy" and its spin-off "Private Practice." While I couldn't find a direct connection between Kate Walsh and the film "Staten Island Summer" or "Saturday Night Live,"}};

To fill the Triplet ({{Staten Island Summer}}-{{cast member}}-?) for the question, we need to determine which entities are most relevant to the question and have a higher likelihood of being the correct answer.You must provide two entities in the answer. please note that the analyzed answer entity should be enclosed in curly brackets {{xxxxxx}}.
In this case, we are looking for an actress who was a cast member of "Saturday Night Live" and starred in the movie "Staten Island Summer." Based on this information, we can eliminate entities that are not actresses or were not cast members of "Saturday Night Live."
The two most relevant entities that meet these criteria are:
{{Cecily Strong}},{{Kate Walsh}}

"""

find_entity_candidates_prompt_wiki2 = """
Question: {}
Triplet:{}
Entites:{}
Related References: 
"""


score_entity_candidates_prompt_wiki = """Please score the entities' contribution to the question on a scale from 0 to 1 (the sum of the scores of all entities is 1).
Q: Staten Island Summer, starred what actress who was a cast member of "Saturday Night Live"?
Relation: cast member
Entites and Related References: 
{{Entity: Ashley Greene}}:{{Reference: is an American actress and model, best known for her role as Alice Cullen in the "Twilight" film series.}}; 
{{Entity: Bobby Moynihan}}:{{Reference: is an American actor and comedian who was a cast member on "Saturday Night Live" from 2008 to 2017. While I couldn't find a direct connection between Bobby Moynihan and the film "Staten Island Summer" }}; 
{{Entity: Camille Saviola}}:{{Reference: is an American actress known for her work in both film and theater. However, there doesn't appear to be a direct connection between Camille Saviola and the question about "Staten Island Summer" and "Saturday Night Live."}}; 
{{Entity: Cecily Strong}}:{{Reference: is an American actress and comedian who is best known as a cast member on "Saturday Night Live." She has been a part of the show since 2012 and has gained recognition for her comedic performances. }}; 
{{Entity: Mary Birdsong}}:{{Reference: is an American actress and comedian. She has appeared in various television shows and films throughout her career. While I couldn't find a direct connection between Mary Birdsong and the film "Staten Island Summer" or "Saturday Night Live"}}
Score: 0.0, 0.4, 0.2, 0.4, 0.0
To score the entities\' contribution to the question, we need to determine which entities are relevant to the question and have a higher likelihood of being the correct answer.
In this case, we are looking for an actress who was a cast member of "Saturday Night Live" and starred in the movie "Staten Island Summer." Based on this information, we can eliminate entities that are not actresses or were not cast members of "Saturday Night Live."
The relevant entities that meet these criteria are:\n- Ashley Greene\n- Bobby Moynihan\n- Camille Saviola\n- Cecily Strong\n- Mary Birdsong\n\nTo distribute the scores, we can assign a higher score to entities that are more likely to be the correct answer. In this case, the most likely answer would be an actress who was a cast member of "Saturday Night Live" around the time the movie was released.
Based on this reasoning, the scores could be assigned as follows:\n- Ashley Greene: 0\n- Bobby Moynihan: 0.4\n- Camille Saviola: 0.2\n- Cecily Strong: 0.4\n- Mary Birdsong: 0.0

Q: {}
Relation: {}
Entites and Related References: 
"""

vanilla_prompt_reasoning_qa_2shot= """
# Task: Given a question, the associated retrieved knowledge, you are asked to answer whether it's sufficient for you to answer the question ({{Yes}} or {{No}}) at the beginning, with these Information and your knowledge. If {{Yes}}, please note that the analyzed answer entity should be enclosed in curly brackets {{xxxxxx}}
# Note that your answer must begin with {{Yes}} or {{No}}. Here are some examples:
# Example1:
Question: 
Viscount Yamaji Motoharu was a general in the early Imperial Japanese Army which belonged to which Empire?
Viscount Yamaji Motoharu was a general in the early Imperial Japanese Army, which belonged to the Empire of Japan. The Empire of Japan was a sovereign state that existed from 1868 to 1947, ruled by the Emperor of Japan.
The Imperial Japanese Army, in which Viscount Yamaji Motoharu served as a general, was the land-based military force of the Empire of Japan during its early years.
During the time when Viscount Yamaji Motoharu held the rank of general, the Empire of Japan was expanding its influence throughout East Asia and engaging in various military campaigns.
As a general in the early Imperial Japanese Army, Viscount Yamaji Motoharu played a role in shaping the military strategies and operations of the Empire of Japan during that period.
The Empire of Japan, under which Viscount Yamaji Motoharu served as a general, had aspirations of regional dominance and pursued an aggressive expansionist policy, leading to conflicts with neighboring countries such as China and Russia.
Answer: 
{Yes}. Based on the given knowledge and my own knowledge, Viscount Yamaji Motoharu, who was a general in the early Imperial Japanese Army, belonged to the Empire of Japan. Therefore, the answer to the question is {Empire of Japan}.

# Example2:
Question: 
Who is the coach of the team owned by Steve Bisciotti?
Retrieved References:
The team owned by Steve Bisciotti is the Baltimore Ravens.
Answer: 
{No}. Based on the given knowledge and my own knowledge, the team owned by Steve Bisciotti is the Baltimore Ravens. Additional knowledge about the specific coach of the Baltimore Ravens is required to answer the question. 

#Now, please carefully consider the following case:
"""



prompt_reasoning_qa_2shot= """

任务：给定问题、关联的检索知识三元组和检索到的句子，请结合这些三元组、相关信息及自身知识，在开头回答是否足以回答问题（{{是}} 或 {{否}}）。若{{是}}，请注意分析的答案实体需用花括号标注 {{xxxxxx}}
注意：回答必须以 {{是}} 或 {{否}} 开头。示例如下：
示例1：
问题：

子爵山路公晴是早期日本帝国陆军将领，该陆军隶属于哪个帝国？

知识三元组：

日本帝国陆军，效忠对象，日本天皇

山路公晴，效忠对象，日本天皇

山路公晴，军衔，将军

检索到的参考文献：

子爵山路公晴是早期日本帝国陆军将领，该陆军隶属于日本帝国。日本帝国是1868年至1947年间存在的君主制国家，由日本天皇统治。

日本帝国陆军（子爵山路公晴曾任将领）是日本帝国早期的陆上武装力量。

在子爵山路公晴担任将领期间，日本帝国正扩张其在东亚的影响力并进行多场军事行动。

作为早期日本帝国陆军将领，子爵山路公晴曾参与制定日本帝国当时的军事战略。

子爵山路公晴担任将领的日本帝国奉行扩张主义政策，谋求地区霸权，导致与中国、俄国等邻国的冲突。

回答：

{是}。根据给定的知识三元组、检索到的句子及自身知识，担任早期日本帝国陆军将领的子爵山路公晴隶属于日本帝国。因此问题答案为{日本帝国}。

示例2：
问题：

史蒂夫·比西奥蒂拥有的球队主教练是谁？

知识三元组：

裸盖菇素，法律归类，鸦片法

鸦片法，包含物质，去甲可待因

橘黄裸伞，上级分类，裸伞属

检索到的参考文献：

史蒂夫·比西奥蒂拥有的球队是巴尔的摩乌鸦队。

回答：

{否}。根据给定的知识三元组、检索到的句子及自身知识，史蒂夫·比西奥蒂拥有的球队是巴尔的摩乌鸦队。需要额外知识才能确定该球队的现任主教练。

现在请仔细分析以下案例：
"""

prompt_reasoning_qa_query_change_2shot="""给定主任务、关联的线索（如果有）、知识三元组（相关事实）和检索到的参考文献（相关文档），请评估当前知识是否足以将主任务分解为子任务（{{是}} 或 {{否}}）。
回答必须以 {是} 或 {否} 开头。
若{是}，请直接列出分解后的子任务，所有子任务用一个方括号标注，且换行给出序号 [1. xxxxxx\n2. xxxxxx]。
若{否}（即知识不足无法分解），需提取出目前已有的部分有助于解决问题的信息 ，用双重花括号包围{{xxxxxx}}。

示例如下：
**示例 1**：
主任务：
优化电商网站的购物车转化率。
线索：无
知识三元组：
购物车转化率, 影响因素, 支付流程复杂度
用户流失, 发生阶段, 付款页面
检索到的参考文献：
A/B测试显示简化支付步骤可提升转化率12%
用户调研表明38%的放弃源于强制注册
**回答**：
{是}。根据当前知识可分解为：[1. 分析现有支付流程瓶颈\n2. 设计免注册快速付款方案\n3. 制定A/B测试方案\n4. 实施用户流失监控]

**示例 2**：
主任务：
开发新型钙钛矿太阳能电池。
线索：无
知识三元组：
太阳能电池, 类型, 硅基
钙钛矿, 化学特性, 光敏性
检索到的参考文献：
MIT团队2023年实现钙钛矿电池25%转化率
**回答**：
{否}。缺失关键知识：当前材料稳定性数据、量产工艺路线、商业化成本模型。已知部分信息为{{钙钛矿具有化学特性光敏性}}

现在请仔细分析以下案例："""


#############################################
"""
给定问题、关联的检索知识三元组和检索到的参考文献，请评估这些资源结合您已有知识是否足以形成答案（{{是}} 或 {{否}}）。
回答必须以 {{是}} 或 {{否}} 开头。
若{{是}}，请注意分析的答案实体必须用花括号标注 {{xxxxxx}}
若{{否}}（即资源无用或提供线索有帮助但不足以下结论），需指出缺失方面并优化搜索查询以精确获取所需信息。优化后的搜索查询同样需用花括号标注 {{xxxxxx}}

示例如下：
**示例 1**：
问题：
子爵山路公晴是早期日本帝国陆军将领，该陆军隶属于哪个帝国？
线索：无
知识三元组：
日本帝国陆军，效忠对象，日本天皇
山路公晴，效忠对象，日本天皇
山路公晴，军衔，将军
检索到的参考文献：
子爵山路公晴是早期日本帝国陆军将领，该陆军隶属于日本帝国。日本帝国是1868年至1947年间存在的君主制国家。
日本帝国陆军（山路公晴曾任将领）是日本帝国早期的陆上武装力量。
在子爵山路公晴担任将领期间，日本帝国正扩张其在东亚的影响力。
作为早期日本帝国陆军将领，山路公晴参与制定了日本帝国当时的军事战略。
山路公晴担任将领的日本帝国奉行扩张主义政策，谋求地区霸权。
**回答**：
{是}。根据给定的知识三元组、检索到的句子及自身知识，担任早期日本帝国陆军将领的子爵山路公晴隶属于日本帝国。因此问题答案为{日本帝国}。

**示例 2**：
问题：
史蒂夫·比西奥蒂拥有的球队主教练是谁？
线索：无
知识三元组：
裸盖菇素，法律归类，鸦片法
鸦片法，包含物质，去甲可待因
橘黄裸伞，上级分类，裸伞属
检索到的参考文献：
史蒂夫·比西奥蒂拥有的球队是巴尔的摩乌鸦队。
史蒂夫·比西奥蒂与其主教练签订了三年合同。
**回答**：
{否}。根据给定的知识三元组、检索到的句子及自身知识，史蒂夫·比西奥蒂拥有的球队是巴尔的摩乌鸦队。需要额外知识才能确定该球队的现任主教练。因此优化线索为{史蒂夫·比西奥蒂拥有的巴尔的摩乌鸦队现任主教练}

现在请仔细分析以下案例：
"""
######################################


prompt_fact_check_clue_3shot = """
# Task: Given a claim, the associated retrieved knowledge Triplets and sentences, you are asked to answer whether the provided references sufficient to verify the claim ({{Yes}} or {{No}}). 
# Note that your answer must begin with {{Yes}} or {{No}}. If you answered {{Yes}}, you must indicate whether the given claim false or true, and enclose the result in curly brackets {{false/true}}. If you answered {{No}}, indicating you are not sure, please respond with NOT ENOUGH INFO, and if applicable, please summarize any insights so far that may be helpful for varify the claim, which must also be enclosed in curly brackets {{xxxxxx}}
# Here are some examples:

# Example 1:
Claim: "Texas is the most populous U.S. state."
Knowledge Triplets:
(Texas, state of, U.S. state)
Retrieved References:
Texas is the second most populous state in the United States, with California being the most populous. 
The population of Texas is approximately 29 million, making it the second most populous state after California.
Answer: {{Yes}}, I can answer. The references explicitly state that Texas is the second most populous state in the United States, with California being the most populous. Therefore, the claim that "Texas is the most populous U.S. state" is incorrect. The answer is {{false}}.

# Example 2:
Claim: "The Eiffel Tower was initially criticized by the famous French writer Guy de Maupassant."
Knowledge Triplets:
(Eiffel Tower, located in, Paris)
(Guy de Maupassant, occupation, writer)
(Eiffel Tower, located in, Paris)
Retrieved References:
Guy de Maupassant, one of France's most famous writers, was known for his vocal criticism of the Eiffel Tower during its construction. He, along with other artists and intellectuals of the time, considered the tower to be an eyesore and unworthy of Paris's aesthetic.
In 1887, Guy de Maupassant joined a group of 300 prominent figures who signed a petition against the tower's construction, arguing that it would ruin the beauty of Paris.
Despite his initial opposition, Guy de Maupassant was later known to dine frequently in the Eiffel Tower's restaurant, claiming it was the only place in Paris where he could avoid seeing the structure he disliked.
Answer:
{{Yes}}, I can answer. The references explicitly state that Guy de Maupassant, a famous French writer, was a vocal critic of the Eiffel Tower during its construction. The references also provide detailed context, including his participation in a petition against the tower and his later ironic behavior of dining in the tower. Therefore, the answer is {{True}}.

# Example 3:
Claim: "The Gadsden flag was named by Christopher Gadsden."
Knowledge Triplets:
(Christopher Gadsden, design, Gadsden flag)
Retrieved References:
Gadsden flag is designed by Christopher Gadsden.
The Gadsden flag is named after politician Christopher Gadsden.
Answer: {{No}}, I can't answer. According to the triples and references, The Gadsden flag is designed by Christopher Gadsden, but there is no information on who named it. 
"""

prompt_reasoning_qa_query_clue_2shot= """
Given a question, some clues, the associated retrieved knowledge triplets and related contexts, you are asked to evaluate if these resources, combined with your pre-existing knowledge, are sufficient to formulate a answer ({{Yes}} or {{No}}).
Your answer must begin with {{Yes}} or {{No}}.
If {{Yes}}, please note that the analyzed answer entity must be enclosed in curly brackets {{xxxxxx}}
If {{No}. which means the resources are useless or provide clues are helpful but insufficient to conclusively answer the question. Based on the given knowledge, if applicable, please summarize any insights so far that may be helpful for answering the question, which must also be enclosed in curly brackets {{xxxxxx}}.

Here are some examples:
### Example 1:
Question: 
The Sentinelese language is the language of people of one of which Islands in the Bay of Bengal ?
(Clues):
None
(Knowledge triplets):
Sentinelese language, indigenous to, Sentinelese people
(Triplet's related context):
The Sentinelese, also known as the Sentineli and the North Sentinel Islanders, are an indigenous people who inhabit North Sentinel Island in the Bay of Bengal in the northeastern Indian Ocean.
(Knowledge triplets):
Bay of Bengal, area, Andaman and Nicobar Islands
(Triplet's related context):
Andaman and Nicobar Islands are an archipelagic island chain in the eastern Indian Ocean across the Bay of Bengal, they are part of India.They are within the union territory of the Andaman and Nicobar Islands 
### Answer: 
{{Yes}} The analyzed answer entity is {{Andaman and Nicobar Islands}}.

### Example 2:
Question: 
Who is the coach of the team owned by the most famous English former professional footballer?
(Clues):
The most famous English former professional footballer is David Beckham.
(Knowledge triplets):
David Beckham, co-owned, Inter Miami CF
(Triplet's related context):
Inter Miami CF, founded in 2018, is a professional soccer club based in Miami, Florida. It competes in Major League Soccer (MLS) as part of the Eastern Conference. David Beckham made a 3 years contract with his major coach.
### Answer: 
{{No}} The Given knowledges provide helpful information that the footballer is David Beckham and David Beckham's ownership of Inter Miami CF, but they do not explicitly mention who the coach is. The useful information for now is {the team owned by the famous English former professional footballer David Beckham is Inter Miami CF}

Now, please carefully consider the following case:
"""

test = """Knowledge 
{
    "Clues": "The most famous English former professional footballer is David Beckham.",
    "Retrieved Knowledge triplets and contexts": [
        {
            "triplet": "David Beckham, co-owned, Inter Miami CF",
            "context": "Inter Miami CF, founded in 2018, is a professional soccer club based in Miami, Florida. It competes in Major League Soccer (MLS) as part of the Eastern Conference. David Beckham made a 3 years contract with his major coach."
        }
    ]
}"""


prompt_reasoning_qa_0shot = """
# Task: Given a question, the associated retrieved knowledge triplets and retrieved sentences, you are asked to answer whether it's sufficient for you to answer the question ({{Yes}} or {{No}}) at the beginning, with these triplets and Related Information and your knowledge. If {{Yes}}, please note that the analyzed answer entity should be enclosed in curly brackets {{xxxxxx}}
# Note that your answer must begin with {{Yes}} or {{No}}. 
# Now, please carefully consider the following case:
"""

prompt_reasoning_fever_0shot = """
# Task: Given a claim, the associated retrieved knowledge triplets and references, you are asked to answer whether the provided references sufficient to verify the claim ({{Yes}} or {{No}}). 
# Note that your answer must begin with {{Yes}} or {{No}}. If you answered {{Yes}}, you must indicate whether the given references SUPPORT or REFUTE the claim, and enclose the result in curly brackets {{SUPPORTS/REFUTES}}. If you answered {{No}}, indicating insufficient evidence, please respond with NOT ENOUGH INFO and enclose the result in curly brackets {{NOT ENOUGH INFO}}.
"""
prompt_reasoning_fever_3shot = """
# Task: Given a claim, the associated retrieved knowledge triplets and references, you are asked to answer whether the provided references sufficient to verify the claim ({{Yes}} or {{No}}). 
# Note that your answer must begin with {{Yes}} or {{No}}. If you answered {{Yes}}, you must indicate whether the given references SUPPORT or REFUTE the claim, and enclose the result in curly brackets {{SUPPORTS/REFUTES}}. If you answered {{No}}, indicating insufficient evidence, please respond with NOT ENOUGH INFO and enclose the result in curly brackets {{NOT ENOUGH INFO}}.
# Here are some examples:

# Example 1:
Claim: "The Great Wall of China is visible from space with the naked eye."
Knowledge Triplets:
(The Great Wall of China, located in, China)
References:
The Great Wall of China, although a massive structure, is not visible to the naked eye from space
The myth that the Great Wall of China is visible from space was debunked
Answer: {{Yes}}, the first sentences explicitly states that the Great Wall is not visible from space with the naked eye. Additionally, the the second sentence confirms that this is a myth and was debunked. The knowledge triplets provide conflicting information, but the references clearly refute the claim. Therefore the answer is {{REFUTES}}

# Example 2:
Claim: "Albert Einstein won the Nobel Prize in Chemistry."
Knowledge Triplets:
(Albert Einstein, won, Nobel Prize in Physics)
References:
Albert Einstein was awarded the Nobel Prize in Physics in 1921.
Knowledge Triplets:
(Nobel Prize in Chemistry, won by, Marie Curie)
References:
Marie Curie was awarded the Nobel Prize in Chemistry in 1911.
Answer: {{No}}, the claim that "Albert Einstein won the Nobel Prize in Chemistry" is not provided by the given references. The Wikipedia page states that Einstein won the Nobel Prize in Physics, not Chemistry. The Nobel Prize site mentions Marie Curie as a recipient of the Chemistry prize. There is insufficient evidence to evaluate the claim. Thus The answer is {{NOT ENOUGH INFO}}.

# Example 3:
Claim: "CRISPR technology can be used to edit genes in human embryos."
Knowledge Triplets:
(CRISPR, used in, gene editing) (Gene editing, possible in, human embryos) (CRISPR, edits, human embryos)
References:
CRISPR-Cas9 has been successfully used to edit genes in human embryos, raising both hopes for curing genetic diseases and ethical concerns.
Recent experiments have demonstrated the potential of CRISPR to edit genes in human embryos, though the technology is still in its experimental stages and surrounded by ethical debates.
Answer: {{Yes}}, the references explicitly states that CRISPR-Cas9 has been used to edit genes in human embryos, mentioning both the scientific success and the ethical implications. The references also confirms this by discussing recent experiments that have demonstrated the potential of CRISPR for gene editing in human embryos, although it notes that the technology is still experimental. The knowledge triplets align with the claim, and the references provide robust evidence to support it. There the answer is {{SUPPORTS}}

# Now, please carefully consider the following case:
"""

vanilla_prompt_fact_check_3shot = """
# Task: Given a claim, the associated retrieved knowledge, you are asked to answer whether the provided references sufficient to verify the claim ({{Yes}} or {{No}}). 
# Note that your answer must begin with {{Yes}} or {{No}}. If you answered {{Yes}}, you must indicate whether the given claim false or true, and enclose the result in curly brackets {{false/true}}. If you answered {{No}}, indicating you are not sure, please respond with NOT ENOUGH INFO and enclose the result in curly brackets {{NOT ENOUGH INFO}}.
# Here are some examples:

# Example 1:
Claim: "Texas is the most populous U.S. state."
Retrieved knowledge:
Texas is the second most populous state in the United States, with California being the most populous. 
The population of Texas is approximately 29 million, making it the second most populous state after California.
Answer: {{Yes}}, I can answer. The references explicitly state that Texas is the second most populous state in the United States, with California being the most populous. Therefore, the claim that "Texas is the most populous U.S. state" is incorrect. The answer is {{false}}.

# Example 2:
Claim: "The Eiffel Tower was initially criticized by the famous French writer Guy de Maupassant."
Retrieved knowledge:
Guy de Maupassant, one of France's most famous writers, was known for his vocal criticism of the Eiffel Tower during its construction. He, along with other artists and intellectuals of the time, considered the tower to be an eyesore and unworthy of Paris's aesthetic.
In 1887, Guy de Maupassant joined a group of 300 prominent figures who signed a petition against the tower's construction, arguing that it would ruin the beauty of Paris.
Despite his initial opposition, Guy de Maupassant was later known to dine frequently in the Eiffel Tower's restaurant, claiming it was the only place in Paris where he could avoid seeing the structure he disliked.
Answer:
{{Yes}}, I can answer. The references explicitly state that Guy de Maupassant, a famous French writer, was a vocal critic of the Eiffel Tower during its construction. The references also provide detailed context, including his participation in a petition against the tower and his later ironic behavior of dining in the tower. Therefore, the answer is {{True}}.

# Example 3:
Claim: "The Gadsden flag was named by Christopher Gadsden."
Retrieved knowledge:
Gadsden flag is designed by Christopher Gadsden.
The Gadsden flag is named after politician Christopher Gadsden.
Answer: {{No}}, I can't answer. According to the knowledge, The Gadsden flag is designed by Christopher Gadsden, but there is no information on who named it. 
"""



prompt_reasoning_fever_3shot_2 = """
# Task: Given a claim, the associated retrieved knowledge triplets and references, you are asked to answer whether the provided references sufficient to verify the claim ({{Yes}} or {{No}}). 
# Note that your answer must begin with {{Yes}} or {{No}}. If you answered {{Yes}}, you must indicate whether the given references SUPPORT or REFUTE the claim, and enclose the result in curly brackets {{SUPPORTS/REFUTES}}. If you answered {{No}}, indicating insufficient evidence, please respond with NOT ENOUGH INFO and enclose the result in curly brackets {{NOT ENOUGH INFO}}.
# Here are some examples:

# Example 1:
Claim: "Texas is the most populous U.S. state."
Knowledge Triplets:
(Texas, state of, U.S. state)
Retrieved References:
Texas is the second most populous state in the United States, with California being the most populous. 
The population of Texas is approximately 29 million, making it the second most populous state after California.
Answer: {{Yes}}, I can answer. The references explicitly state that Texas is the second most populous state in the United States, with California being the most populous. Therefore, the claim that "Texas is the most populous U.S. state" is incorrect. The answer is {{REFUTES}}.

# Example 2:
Claim: "The Eiffel Tower was initially criticized by the famous French writer Guy de Maupassant."
Knowledge Triplets:
(Eiffel Tower, located in, Paris)
(Guy de Maupassant, occupation, writer)
(Eiffel Tower, located in, Paris)
Retrieved References:
Guy de Maupassant, one of France's most famous writers, was known for his vocal criticism of the Eiffel Tower during its construction. He, along with other artists and intellectuals of the time, considered the tower to be an eyesore and unworthy of Paris's aesthetic.
In 1887, Guy de Maupassant joined a group of 300 prominent figures who signed a petition against the tower's construction, arguing that it would ruin the beauty of Paris.
Despite his initial opposition, Guy de Maupassant was later known to dine frequently in the Eiffel Tower's restaurant, claiming it was the only place in Paris where he could avoid seeing the structure he disliked.
Answer:
{{Yes}}, I can answer. The references explicitly state that Guy de Maupassant, a famous French writer, was a vocal critic of the Eiffel Tower during its construction. The references also provide detailed context, including his participation in a petition against the tower and his later ironic behavior of dining in the tower. Therefore, the answer is {{SUPPORTS}}.

# Example 3:
Claim: "The Gadsden flag was named by Christopher Gadsden."
Knowledge Triplets:
(Christopher Gadsden, design, Gadsden flag)
Retrieved References:
Gadsden flag is designed by Christopher Gadsden.
The Gadsden flag is named after politician Christopher Gadsden.
Answer: {{No}}, I can't answer. According to the triples and references, The Gadsden flag is designed by Christopher Gadsden, but there is no information on who named it. 
"""

prompt_reasoning_qa_query_change_0shot = """
Given a question, the associated retrieved knowledge triplets and retrieved references, you are asked to evaluate if these resources, combined with your pre-existing knowledge, are sufficient to formulate a answer ({{Yes}} or {{No}}).
If {{Yes}}, please note that the analyzed answer entity must be enclosed in curly brackets {{xxxxxx}}
If {No}, it means the resources are useless or provide clues that are helpful but insufficient to answer the question conclusively. Based on the given knowledge, please summarize any insights (if any) so far that may help answer the question, which must also be enclosed in curly brackets{xxxxxx}"""

triple_translation_1shot = """You are asked to convert a knowledge graph (KG) triplet chain into natural language.
Here's an example:
### Input:
(Thomas Edison, invented, light bulb)
(light bulb, uses, electricity)
(electricity, discovered by, Michael Faraday)
### Output:
Thomas Edison invented the light bulb, which uses electricity, a fundamental discovery made by Michael Faraday.

Now, please carefully consider the following case:
### Input: 
{}
### Output:
"""

reasoning_zero_shot_doc = """
Given a question and some references materials, try to find the answer from it.
The reference materials do not guarantee the inclusion of answer information. Thus You also need to identify the domain of the question and combine your own knowledge in that domain to answer.
Please note that 1. Be careful with your answers, and if you cannot provide the correct answer, you must say you do not know. 2. Some questions are factually incorrect and cannot be answered, such as 'When did Musk sell Twitter?', while Musk has not sold Twitter. In this case, you need to figure out the factual incorrect of the question, and you must be careful to identify this situation.
### Question
{query}
### References 
{references}
 ### Answer
"""

extract_all_relation_json_prompt = """
# Task: 
Carefully review the question provided.
From the list of available relations for their corresponding entity, select the %s that you believe are most likely to link to the entities that can provide the most relevant information to help answer the provided question.
For each given entity, which derives from Wikipedia Knowledge Graph, select the %s relations that are most likely to link to relevant entities that can provide useful information to help answer the provided question respectively. 
For each selected relation, provide a score from 0 to 10 rating its contribution to answering the question respectively.


"""
# 3个%s -> width
extract_all_relation_prompt_wiki = """
# Task: 
1. Carefully review the question provided.
2. From the list of available relations for their corresponding entity, select the %s that you believe are most likely to link to the entities that can provide the most relevant information to help answer the provided question.
3. For each selected relation, provide a score between 0 to 10 reflecting its usefulness in answering the question, with 10 being most useful.
4. Provide a brief explanation for your choices, highlighting how each selected relation potentially contributes to answering the question.

# The input follows below format:
Question:[The question text]
Entity 1:[The name of the entity 1]
Available Relations:[A relation list of entity 1 to be chosen.]
Entity 2:[The name of the entity 2]:
Available Relations:[A relation list of entity 2 to be chosen.]
...(Continue in the same manner for additional entities)

# Below is two examples:
# Example1:
Question: Mesih Pasha's uncle became emperor in what year?
Topic Entity: Mesih Pasha
Relations:
1. wiki.relation.child
2. wiki.relation.country_of_citizenship
3. wiki.relation.date_of_birth
4. wiki.relation.family
5. wiki.relation.father
6. wiki.relation.languages_spoken, written_or_signed
7. wiki.relation.military_rank
Answer: 
1. {wiki.relation.family (Score: 1.0)}: This relation is highly relevant as it can provide information about the family background of Mesih Pasha, including his uncle who became emperor.
2. {wiki.relation.father (Score: 0.4)}: Uncle is father's brother, so father might provide some information as well.
3. ......

# Example2:
Question: what the attitude of Joe Biden towards China?
Entity 1: china
Relations:
1. wiki.relation.alliance
2. wiki.relation.international_relation
3. wiki.relation.political_system
4. wiki.relation.population
Entity 2: joe biden
Relations:
1. wiki.relation.political_position
2. wiki.relation.presidency
3. wiki.relation.family
4. wiki.relation.early_life

Answer:
Entity 1: 
1. {wiki.relation.alliance (Score: 8)}: This relation is highly relevant as it can provide information about the relationship between china and other parties.
2. {wiki.relation.political_system (Score: 7)}:  This relation is relevant as it can provide information about the policies that might reflect the relationship between china and other parties.
3. ......
Entity 2: 
1. {wiki.relation.political_position (Score: 10)}: This relation is highly relevant as it can provide information about joe biden's political position to other parties or countries.
2. {wiki.relation.presidency (Score: 2)}: This relation is slightly relevant as it can provide information about joe biden's position, which might provide clues to answer the question.
3. ......

# For questions involving multiple entities, you are required to analyze the relation list for each entity separately. Then select the %s most relevant relations for each entity, based on the analysis as done in the given example. 
# It's essential to maintain strict adherence to the line breaks and format as seen in the provided example for clarity and consistency:

Answer: 
Entity 1: The Name of Entity 1
1. {Relation1 (Score: X)}: Explanation.
2. {Relation2 (Score: Y)}: Explanation.

Entity 2: The Name of Entity 2
1. {Relation1 (Score: X)}: Explanation
2. {Relation2 (Score: Y)}: Explanation

...(Continue in the same manner for additional entities)

# 请严格按照以下格式输出，不要包含其他解释性内容：

Answer: 
Entity: [实体1名称]
1. {关系名称 (Score: X.X)}: 解释
2. {关系名称 (Score: X.X)}: 解释

Entity: [实体2名称]
1. {关系名称 (Score: X.X)}: 解释

## 重要要求：
1. 必须以"Answer:"开头
2. 每个实体行以"Entity: [实体名称]"开始
3. 不要添加任何额外的标题或解释文本
4. 不要在关系名称前添加序号

# Now, I will provide you a new question with %s entities and relations. Please analyse it following all the guidance above carefully. 

Question: """


extract_all_relation_prompt_wiki_cn ="""
# 任务: 
1. 仔细分析用户提出的问题
2. 从对应实体可用的关系列表中，选择 %s 个你认为最可能链接到能够回答问题所需信息的关系
3. 为每个选中的关系提供0-10分的相关性评分(10分表示最相关)
4. 简要解释选择理由，说明该关系如何有助于回答问题

# 输入格式:
问题: [问题文本]
实体 1: [实体1名称]
可用关系: [实体1的可选关系列表]
实体 2: [实体2名称]
可用关系: [实体2的可选关系列表]
...(按此格式继续处理其他实体)

# 下面是两个示例(英文):
# 示例1:
Question: Mesih Pasha's uncle became emperor in what year?
Topic Entity: Mesih Pasha
Relations:
1. wiki.relation.child
2. wiki.relation.country_of_citizenship
3. wiki.relation.date_of_birth
4. wiki.relation.family
5. wiki.relation.father
6. wiki.relation.languages_spoken, written_or_signed
7. wiki.relation.military_rank
Answer: 
1. {wiki.relation.family (Score: 1.0)}: This relation is highly relevant as it can provide information about the family background of Mesih Pasha, including his uncle who became emperor.
2. {wiki.relation.father (Score: 0.4)}: Uncle is father's brother, so father might provide some information as well.
3. ......

# 示例2:
Question: what the attitude of Joe Biden towards China?
Entity 1: china
Relations:
1. wiki.relation.alliance
2. wiki.relation.international_relation
3. wiki.relation.political_system
4. wiki.relation.population
Entity 2: joe biden
Relations:
1. wiki.relation.political_position
2. wiki.relation.presidency
3. wiki.relation.family
4. wiki.relation.early_life

Answer:
Entity 1: 
1. {wiki.relation.alliance (Score: 8)}: This relation is highly relevant as it can provide information about the relationship between china and other parties.
2. {wiki.relation.political_system (Score: 7)}:  This relation is relevant as it can provide information about the policies that might reflect the relationship between china and other parties.
3. ......
Entity 2: 
1. {wiki.relation.political_position (Score: 10)}: This relation is highly relevant as it can provide information about joe biden's political position to other parties or countries.
2. {wiki.relation.presidency (Score: 2)}: This relation is slightly relevant as it can provide information about joe biden's position, which might provide clues to answer the question.
3. ......

# 当问题涉及多个实体时，您需要为每个实体单独分析其关系列表。然后按照示例为每个实体选择 %s 个最相关的关系
# 为了保持格式清晰一致，请严格遵循以下格式规范：

Answer: 
Entity: [实体1名称]
1. {关系名称 (Score: X)}: 解释.
2. {关系名称 (Score: Y)}: 解释.

Entity: [实体2名称]
1. {关系名称 (Score: X)}: 解释
2. {关系名称 (Score: Y)}: 解释

...(按此格式继续处理其他实体)

# 严格输出规范：
1. 必须以"Answer:"开头
2. 每个实体行必须以"Entity: [实体名称]"开始
3. 禁止添加任何额外的标题或解释文本
4. 关系名称前不要添加序号
5. 必须使用原始提供的关系名称(不要翻译或修改)
6. 评分必须使用数字格式(如: 8.5, 7.0)
7. 整个输出只包含指定格式的关系项

# 现在请分析以下包含 %s 个实体的问题(将使用原始提供的关系名称):
Question: 
"""


extract_relation_prompt_wiki = """Please retrieve %s relations (separated by semicolon) that contribute to the question and rate their contribution on a scale from 0 to 1.
Question: Mesih Pasha's uncle became emperor in what year?
Topic Entity: Mesih Pasha
Relations:
1. child
2. country_of_citizenship
3. date_of_birth
4. family
5. father
6. languages_spoken
7. military_rank
8. occupation
9. place_of_death
10. position_held

Answer: 
1. {family (Score: 1.0)}: This relation is highly relevant as it can provide information about the family background of Mesih Pasha, including his uncle who became emperor.
2. {father (Score: 0.4)}: Uncle is father's brother, so father might provide some information as well.
3. {position held (Score: 0.1)}: This relation is moderately relevant as it can provide information about any significant positions held by Mesih Pasha or his uncle that could be related to becoming an emperor.
4. ......

Question: Van Andel Institute was founded in part by what American businessman, who was best known as co-founder of the Amway Corporation?
Topic Entity: Van Andel Institute
Relations:
1. wiki.relation.affiliation
2. wiki.relation.country
3. wiki.relation.donations
4. wiki.relation.educated_at
5. wiki.relation.employer

Answer: 
1. {wiki.relation.affiliation (Score: 0.8)}: This relation is relevant because it can provide information about the individuals or organizations associated with the Van Andel Institute, including the American businessman who co-founded the Amway Corporation.
2. {wiki.relation.donations (Score: 0.3)}: This relation is relevant because it can provide information about the financial contributions made to the Van Andel Institute, which may include donations from the American businessman in question.
3. {wiki.relation.educated_at (Score: 0.3)}: This relation is relevant because it can provide information about the educational background of the American businessman, which may have influenced his involvement in founding the Van Andel Institute.
4. ......

Question: """


answer_prompt_wiki = """Given a question and the associated retrieved knowledge graph triplets (entity, relation, entity) and Related Informations, you are asked to answer the question with these triplets,Informations and your own knowledge.Please note that the analyzed answer entity should be enclosed in curly brackets. The Template final sentence of the response is: Therefore, the answer to the question is {{xxxxxxx}}.

Q: Viscount Yamaji Motoharu was a general in the early Imperial Japanese Army which belonged to which Empire?

Knowledge Triplets: 
Imperial Japanese Army, allegiance, Emperor of Japan
Yamaji Motoharu, allegiance, Emperor of Japan
Yamaji Motoharu, military rank, general

Related Information:
Viscount Yamaji Motoharu was a general in the early Imperial Japanese Army, which belonged to the Empire of Japan. The Empire of Japan was a sovereign state that existed from 1868 to 1947, ruled by the Emperor of Japan.
The Imperial Japanese Army, in which Viscount Yamaji Motoharu served as a general, was the land-based military force of the Empire of Japan during its early years.
During the time when Viscount Yamaji Motoharu held the rank of general, the Empire of Japan was expanding its influence throughout East Asia and engaging in various military campaigns.
As a general in the early Imperial Japanese Army, Viscount Yamaji Motoharu played a role in shaping the military strategies and operations of the Empire of Japan during that period.
The Empire of Japan, under which Viscount Yamaji Motoharu served as a general, had aspirations of regional dominance and pursued an aggressive expansionist policy, leading to conflicts with neighboring countries such as China and Russia.

A: Based on the given knowledge triplets and my knowledge, Viscount Yamaji Motoharu, who was a general in the early Imperial Japanese Army, belonged to the Empire of Japan. Therefore, the answer to the question is {Empire of Japan}.

"""

cot_prompt = """Q: 哪所大学以乔治·华盛顿殖民者男子篮球队代表其体育项目？

A: 第一，拥有名为乔治·华盛顿殖民者男子篮球队的教育机构是乔治·华盛顿大学。第二，乔治·华盛顿大学位于华盛顿特区。答案是{华盛顿特区}。

Q: 谁将普罗玛莎·乔杜里列为影响者并创作了《人民的意志》？

A: 第一，《人民的意志》由Bharoto Bhagyo Bidhata创作。第二，Bharoto Bhagyo Bidhata将普罗玛莎·乔杜里列为影响者。答案是{Bharoto Bhagyo Bidhata}。

Q: 哪位艺人因《你让我疯狂》获得奖项提名？

A: 第一，因《你让我疯狂》获得奖项提名的艺人是布兰妮·斯皮尔斯。答案是{杰森·艾伦·亚历山大}。

Q: 哪位出生于锡根的人物影响了文森特·梵高的作品？

A: 第一，彼得·保罗·鲁本斯、克劳德·莫奈等人影响了文森特·梵高的作品。第二，彼得·保罗·鲁本斯出生于锡根。答案是{彼得·保罗·鲁本斯}。

Q: 哪个与俄罗斯接壤的国家由米哈伊尔·萨卡什维利担任政府职务？

A: 第一，中国、挪威、芬兰、爱沙尼亚和格鲁吉亚与俄罗斯接壤。第二，米哈伊尔·萨卡什维利在格鲁吉亚担任政府职务。答案是{格鲁吉亚}。

Q: 饰演尿烷轮子男角色的演员因哪种药物过量？

A: 第一，米切尔·李·赫德伯格饰演尿烷轮子男角色。第二，米切尔·李·赫德伯格因海洛因过量。答案是{海洛因}。"""

only_with_sentences_prompt = """
Given a question and Related Informations, you are asked to answer the question with Informations and your own knowledge.Please note that the analyzed answer entity should be enclosed in curly brackets. The Template final sentence of the response is: Therefore, the answer to the question is {{xxxxxxx}}.

Q: What state is home to the university that is represented in sports by George Washington Colonials men's basketball?
Related Information:
The university represented in sports by the George Washington Colonials men's basketball team is located in Washington, D.C., which is not technically a state but the capital of the United States.
The George Washington Colonials men's basketball team represents George Washington University, which is located in the District of Columbia, the same location as the nation's capital.
The George Washington Colonials men's basketball team is based in Foggy Bottom, a neighborhood in Washington, D.C., where George Washington University is situated.
George Washington University, the home of the Colonials men's basketball team, is located in the heart of downtown Washington, D.C., near famous landmarks such as the White House and the National Mall.
The George Washington Colonials men's basketball team is affiliated with George Washington University, an esteemed educational institution situated in Washington, D.C., renowned for its academic programs as well as its athletic teams.

A: First, the education institution has a sports team named George Washington Colonials men's basketball in is George Washington University , Second, George Washington University is in Washington D.C. The answer is {Washington, D.C.}.

Q: Who lists Pramatha Chaudhuri as an influence and wrote Jana Gana Mana?
Related Information:
Rabindranath Tagore lists Pramatha Chaudhuri as an influence and wrote Jana Gana Mana. Tagore, the renowned poet, philosopher, and Nobel laureate, was greatly influenced by Pramatha Chaudhuri, a prominent writer, critic, and editor in Bengal during the early 20th century.
Jana Gana Mana, the national anthem of India, was written by Rabindranath Tagore, who acknowledged Pramatha Chaudhuri as one of his influences. Chaudhuri's literary works and ideas had a profound impact on Tagore's creative journey.
Pramatha Chaudhuri's literary contributions and intellectual discussions played a significant role in shaping Rabindranath Tagore's artistic development. Tagore admired Chaudhuri's writings and sought inspiration from his literary perspectives.
In his autobiographical writings, Rabindranath Tagore often mentioned Pramatha Chaudhuri as one of the influential figures who shaped his thoughts and writings, including the composition of Jana Gana Mana.
The intellectual exchanges between Rabindranath Tagore and Pramatha Chaudhuri enriched both their literary pursuits. Tagore's admiration for Chaudhuri's ideas is evident in his acknowledgment of Chaudhuri as an influence and his composition of Jana Gana Mana reflects this creative association.

A: First, Bharoto Bhagyo Bidhata wrote Jana Gana Mana. Second, Bharoto Bhagyo Bidhata lists Pramatha Chaudhuri as an influence. The answer is {Bharoto Bhagyo Bidhata}.
"""

only_with_gpt_prompt = """
Given a question, you are asked to answer the question with your own knowledge.
Question: """

aa = """
# Task: For each given entity in Wikipedia Knowledge Graph, select the %s relations that are most likely to link to relevant entities that can provide useful information to help answer the provided question. For each selected relation, provide a score from 0 to 10 rating its contribution to answering the question.

# The input follows below format:
Question:[The question text]
Entity 1:[The name of the entity 1]
Available Relations:[A relation list of entity 1 to be chosen.]
Entity 2:[The name of the entity 2]:
Available Relations:[A relation list of entity 2 to be chosen.]
...(Continue in the same manner for additional entities)

# Below is an example of a simple input containing only one entity.
# Example:

Question: Mesih Pasha's uncle became emperor in what year?
Entity 1: Mesih Pasha
Available Relations:
1. child
2. country_of_citizenship
3. position_held
4. family
5. father
6. languages_spoken, written_or_signed
7. military_rank
8. occupation
9. place_of_death

Answer:
Entity 1: Mesih Pasha
1. {family (Score: 10)}: This relation is highly relevant as it can provide information about the family background of Mesih Pasha, including his uncle who became emperor.
2. {father (Score: 4)}: Uncle is father's brother, so father might provide some information as well.
3. {position held (Score: 1)}: This relation is moderately relevant as it can provide information about any significant positions held by Mesih Pasha or his uncle that could be related to becoming an emperor.
4. ...

#The example previously shown a simple example handling an input with a singular entity. For questions involving multiple entities, you are required to analyze the relation list for each entity separately. Then select the %s most relevant relations for each entity, based on the analysis as done in the given example. 
# Instructions:
1. Carefully review the question provided.
2. From the list of available relations for their corresponding entity, select the %s that you believe are most likely to link to the entities that can provide the most relevant information to help answer the provided question.
3. For each selected relation, provide a score between 0 to 10 reflecting its usefulness in answering the question, with 10 being most useful.
4. Provide a brief explanation for your choices, highlighting how each selected relation contributes to answering the question.
5. It's essential to maintain strict adherence to the line breaks and format as seen in the provided example for clarity and consistency. 
6. Especially, DO NOT change any character of given relations!!!

Answer: 
Entity 1: The Name of Entity 1
1. {Relation1 (Score: X)}: Explanation.
2. {Relation2 (Score: Y)}: Explanation.

Entity 2: The Name of Entity 2
1. {Relation1 (Score: X)}: Explanation
2. {Relation2 (Score: Y)}: Explanation

...(Continue in the same manner for additional entities)

# Now, I will provide you a new qusestion with entities and relations. Please analyse it following all the guidance above carefully. 

Question: """

topic_prune_demos = '''
Given a question and a group of related topic entities derived from the Wikipedia knowledge graph, the task is to select which of these entities are suitable as starting points for reasoning on the wiki knowledge graph to find information and clues that are useful for answering the question. 
Note that your output should be strictly Json formatted: {id: entity}. 
Here are examples showing how to analyse and output a Json formatted answer:

Example 1:
question: What major city is the Faith Lutheran Middle School and High School located by?
topic entities: {
    "Q111": "Faith Lutheran Middle School",
    "Q39722": "Faith Lutheran High School"
}
Analysis: 
All entities are directly related to the core of the question—finding the possibale information about Faith Lutheran and its location.
Output: 
{"Q111": "Faith Lutheran Middle School"，"Q39722": "Faith Lutheran High School"}

Example 2:
question: How many Turkish verbs ending with “uş” with their lemma.
topic entities: {
    "Q24905": "verb"
}
Analysis: 
Q24905 "verb" focuses on verbs, which are action words in a language. The task involves not just identifying verbs but specifically Turkish verbs that end with the suffix "uş,". Therefore, the entity "verb" is too broad and does not point to a specific Turkish verbs. Thus there is no suitable topic entity as a starting point for reasoning. 
Output: 
{}

Example 3:
question: On which island is the Indonesian capital located?
topic entities: {
    "Q252": "Indonesia",
    "Q23442": "island"
}
Analysis: 
Q252 "Indonesia" represents the country of Indonesia. Considering the question is about the capital of Indonesia and which island it is located on, the entity "Indonesia" is directly related to the core of the question—finding the capital of Indonesia and then identifying the island it is situated on. Therefore, this entity is highly suitable as a starting point for reasoning. 
Q23442 "island" represents the concept of an island. While the question does indeed relate to an island, the concept of "island" itself is too broad and does not point to a specific geographical location or country. From the perspective of reasoning on a knowledge graph, trying to find the capital of a specific country based solely on the concept of an island is less relevant and efficient compared to starting from that country. 
Hence, Q252 "Indonesia" is the more suitable topic entity as a starting point for reasoning on the knowledge graph. It directly connects to the key information of the question and can effectively guide the search for entities related to the answer within the knowledge graph.
Output: 
{"Q252": "Indonesia"}
'''

topic_prune_demos_new ="""
{
  "任务描述": "给定一个问题以及一组从维基百科知识图谱中提取的相关主题实体，请从中选择适合作为推理起点的实体，以便在知识图谱中寻找有助于回答问题的信息和线索。",
  "输出要求": {
    "格式": "严格的 JSON 格式",
    "结构": {
      "selected_entities": "选中的实体列表"
    },
    "示例": [
      {
        "输入": {
          "question": "Faith Lutheran Middle School and High School 位于哪个主要城市附近？",
          "topic_entities": ["Faith Lutheran Middle School", "Faith Lutheran High School"]
        },
        "分析": "所有实体都与问题的核心直接相关——寻找 Faith Lutheran 及其位置的可能信息",
        "输出": {"selected_entities": ["Faith Lutheran Middle School", "Faith Lutheran High School"]}
      },
      {
        "输入": {
          "question": "有多少土耳其动词以 'uş' 结尾，并给出它们的原形？",
          "topic_entities": ["verb"]
        },
        "分析": "实体 'verb' 过于宽泛，无法指向特定的土耳其语动词，没有合适的主题实体作为推理起点",
        "输出": {"selected_entities": []}
      },
      {
        "输入": {
          "question": "印度尼西亚的首都位于哪个岛屿？",
          "topic_entities": ["Indonesia", "island"]
        },
        "分析": "'Indonesia' 直接关联问题核心，而 'island' 过于宽泛无法指向特定地理位置",
        "输出": {"selected_entities": ["Indonesia"]}
      }
    ]
  },
  "当前任务": {
    "question": "{{question}}",
    "topic_entities": {{entities}},
    "分析要点": [
      "1. 实体是否直接关联问题核心内容",
      "2. 实体是否过于宽泛无法提供具体信息",
      "3. 实体是否能作为知识图谱推理的有效起点",
      "4. 选择最相关且能引导有效推理的实体"
    ],
    "输出要求": "必须返回 JSON 格式，包含 'selected_entities' 字段"
  }
}"""



hotpotqa_s1_prompt_demonstration = """

严格遵循以下示例格式，在回答问题前提供两条推理。

Q: 这位在2014年巴林GP2系列赛中获得季军的英国赛车手出生于哪一年？

A: 第一，在2014年巴林GP2系列赛中，DAMS车队车手乔利恩·帕尔默获得季军。第二，乔利恩·帕尔默（1991年1月20日出生）是英国赛车手。答案为1991。

Q: 安东尼·金合作的乐队中，哪个乐队于1985年在曼彻斯特成立？

A: 第一，安东尼·金曾任Simply Red乐队录音室工程师。第二，Simply Red乐队于1985年在曼彻斯特成立。答案为Simply Red。

Q: 阿尔伯塔·菲雷蒂工作室所在城市邻近地区有多少居民？

A: 第一，阿尔伯塔·菲雷蒂工作室位于里米尼附近。第二，里米尼市人口为146,606人。答案为146,606。

"""


fever_s1_prompt_demonstration = """

判断是否存在支持（SUPPORTS）或反驳（REFUTES）主张的观察证据，或信息不足（NOT ENOUGH INFO）。严格遵循以下示例格式，在回答问题前提供两条推理。

Q: 加兹登旗帜由克里斯托弗·加兹登命名。

A: 第一，加兹登旗帜以政治家克里斯托弗·加兹登命名。第二，无关于命名者身份的信息。答案为信息不足。

Q: 雷格·沃森是现任电视制片人。

A: 第一，雷金纳德·詹姆斯·沃森AM是澳大利亚电视制片人及编剧。第二，雷金纳德·詹姆斯·沃森AM于2019年10月8日逝世。答案为反驳。

Q: 《黑镜》讲述社会议题。

A: 第一，《黑镜》是英国选集式电视连续剧。第二，该剧通过科技手段评论当代社会问题。答案为支持。

"""

fever_s1_prompt_demonstration_6_shot = """
Determine if there is Observation that SUPPORTS or REFUTES a Claim, or if there is NOT ENOUGH INFO. Strictly follow the format of the below examples, provide two rationales before answering the question.
Q: The Gadsden flag was named by Christopher Gadsden.
A: First, The Gadsden flag is named after politician Christopher Gadsden. Second, there is no information on who named the Gadsden flag. The answer is NOT ENOUGH INFO.

Q: Reg Watson is a current television producer.
A: First, Reginald James Watson AM was an Australian television producer and screenwriter. Second, Reginald James Watson AM died on 8 October 2019. The answer is REFUTES.

Q: Black Mirror is about society.
A: First, Black Mirror is a British anthology television series. Second, The series uses technology to comment on contemporary social issues. The answer is SUPPORTS.

Q: Shahid Kapoor has acted professionally.
A: First, Shahid Kapoor is an Indian actor who appears in Hindi films. Second, there is no information on how he acted. The answer is NOT ENOUGH INFO.

Q: Sierra Leone's first Bishop was Sir Milton Margai.
A: First, Sir Milton Augustus Strieby Margai PC was a Sierra Leonean medical doctor and politician. Second, there is no information on him being the bishop. The answer is NOT ENOUGH INFO.

Q: True Detective's second season was set in the most populous state of the United States.
A: First, True Detective is an American anthology crime drama television series. Its second season is set in California. Second, California is the most populous U.S. state. The answer is SUPPORTS.

"""


prompt_reasoning_fever_query_change_3shot = """
# Task: Given a claim, the associated retrieved knowledge triplets and references, you are asked to answer whether the provided references sufficient to verify the claim ({{Yes}} or {{No}}). 
# Note that your answer must begin with {{Yes}} or {{No}}. If you answered {{Yes}}, you must indicate whether the given references SUPPORT or REFUTE the claim, and enclose the result in curly brackets {{SUPPORTS/REFUTES}}. If {No}, it means the resources are useless or provide clues that are helpful but insufficient to answer the question conclusively. Based on the given knowledge, please summarize any insights (if any) so far that may help answer the question, which must also be enclosed in curly brackets{xxxxxx}
# Here are some examples:

# Example 1:
Claim: "The Great Wall of China is visible from space with the naked eye."
Clues: None
Knowledge Triplets:
(The Great Wall of China, located in, China)
Retrieved References:
The Great Wall of China, although a massive structure, is not visible to the naked eye from space
The myth that the Great Wall of China is visible from space was debunked
Answer: {{Yes}}, the first sentences explicitly states that the Great Wall is not visible from space with the naked eye. Additionally, the the second sentence confirms that this is a myth and was debunked. The knowledge triplets provide conflicting information, but the references clearly refute the claim. Therefore the answer is {{REFUTES}}

# Example 2:
Claim: "CRISPR technology can be used to edit genes in human embryos."
Clues: None
Knowledge Triplets:
(CRISPR, used in, gene editing)
(CRISPR, edits, human embryos)
(Gene editing, possible in, human embryos)
Retrieved References:
CRISPR-Cas9 has been successfully used to edit genes in human embryos, raising both hopes for curing genetic diseases and ethical concerns.
Recent experiments have demonstrated the potential of CRISPR to edit genes in human embryos, though the technology is still in its experimental stages and surrounded by ethical debates.
Answer: {{Yes}}, the references explicitly states that CRISPR-Cas9 has been used to edit genes in human embryos, mentioning both the scientific success and the ethical implications. The references also confirms this by discussing recent experiments that have demonstrated the potential of CRISPR for gene editing in human embryos, although it notes that the technology is still experimental. The knowledge triplets align with the claim, and the references provide robust evidence to support it. There the answer is {{SUPPORTS}}

# Example 3:
Claim: "Albert Einstein won the Nobel Prize in Chemistry."
Clues: None
Knowledge Triplets:
(Albert Einstein, won, Nobel Prize in Physics)
(Nobel Prize in Chemistry, won by, Marie Curie)
Retrieved References:
Albert Einstein was awarded the Nobel Prize in Physics in 1921.
Nobel Prize official site: "Marie Curie was awarded the Nobel Prize in Chemistry in 1911.
Answer: {{No}}, the claim that "Albert Einstein won the Nobel Prize in Chemistry" is not provided by the given references. The Wikipedia page states that Einstein won the Nobel Prize in Physics, not Chemistry. The Nobel Prize site mentions Marie Curie as a recipient of the Chemistry prize. There is insufficient evidence to evaluate the claim. Therefore uesful clues so far is {{Einstein won the Nobel Prize in Physics, not Chemistry}}.

# Now, please carefully consider the following case:
"""

prompt_reasoning_fever_query_change_6shot = """
# Task: Given a claim, the associated retrieved knowledge triplets and references, you are asked to answer whether the provided references sufficient to verify the claim ({{Yes}} or {{No}}). 
# Note that your answer must begin with {{Yes}} or {{No}}. If you answered {{Yes}}, you must indicate whether the given references SUPPORT or REFUTE the claim, and enclose the result in curly brackets {{SUPPORTS/REFUTES}}. If {No}, it means the resources are useless or provide clues that are helpful but insufficient to answer the question conclusively. Based on the given knowledge, please summarize any insights (if any) so far that may help answer the question, which must also be enclosed in curly brackets{xxxxxx}
# Here are some examples:

# Example 1:
Claim: "The Great Wall of China is visible from space with the naked eye."
Clues: None
Knowledge Triplets:
(The Great Wall of China, located in, China)
Retrieved References:
The Great Wall of China, although a massive structure, is not visible to the naked eye from space
The myth that the Great Wall of China is visible from space was debunked
Answer: {{Yes}}, I can answer. The first sentences explicitly states that the Great Wall is not visible from space with the naked eye. Additionally, the the second sentence confirms that this is a myth and was debunked. The knowledge triplets provide conflicting information, but the references clearly refute the claim. Therefore the answer is {{REFUTES}}

# Example 2:
Claim: "CRISPR technology can be used to edit genes in human embryos."
Clues: None
Knowledge Triplets:
(CRISPR, used in, gene editing)
(CRISPR, edits, human embryos)
(Gene editing, possible in, human embryos)
Retrieved References:
CRISPR-Cas9 has been successfully used to edit genes in human embryos, raising both hopes for curing genetic diseases and ethical concerns.
Recent experiments have demonstrated the potential of CRISPR to edit genes in human embryos, though the technology is still in its experimental stages and surrounded by ethical debates.
Answer: {{Yes}}, I can answer. The references explicitly states that CRISPR-Cas9 has been used to edit genes in human embryos, mentioning both the scientific success and the ethical implications. The references also confirms this by discussing recent experiments that have demonstrated the potential of CRISPR for gene editing in human embryos, although it notes that the technology is still experimental. The knowledge triplets align with the claim, and the references provide robust evidence to support it. There the answer is {{SUPPORTS}}

# Example 3:
Claim: "Albert Einstein won the Nobel Prize in Chemistry."
Clues: None
Knowledge Triplets:
(Albert Einstein, won, Nobel Prize in Physics)
(Nobel Prize in Chemistry, won by, Marie Curie)
Retrieved References:
Albert Einstein was awarded the Nobel Prize in Physics in 1921.
Nobel Prize official site: "Marie Curie was awarded the Nobel Prize in Chemistry in 1911.
Answer: {{No}}, I can't answer. The claim that "Albert Einstein won the Nobel Prize in Chemistry" is not provided by the given references. The reference states that Einstein won the Nobel Prize in Physics, not Chemistry. The Nobel Prize site mentions Marie Curie as a recipient of the Chemistry prize. There is insufficient evidence to evaluate the claim. Therefore uesful clues so far is {{Einstein won the Nobel Prize in Physics, not Chemistry}}.

# Example 4:
Claim: "Texas is the most populous U.S. state."
Clues: None
Knowledge Triplets:
(Texas, state of, U.S. state)
Retrieved References:
Texas is the second most populous state in the United States, with California being the most populous. 
The population of Texas is approximately 29 million, making it the second most populous state after California.
Answer: {{Yes}}, I can answer. The references explicitly state that Texas is the second most populous state in the United States, with California being the most populous. Therefore, the claim that "Texas is the most populous U.S. state" is incorrect. The answer is {{REFUTES}}.

# Example 5:
Claim: "The Eiffel Tower was initially criticized by the famous French writer Guy de Maupassant."
Clues: None
Knowledge Triplets:
(Eiffel Tower, located in, Paris)
(Guy de Maupassant, occupation, writer)
(Eiffel Tower, located in, Paris)
Retrieved References:
Guy de Maupassant, one of France's most famous writers, was known for his vocal criticism of the Eiffel Tower during its construction. He, along with other artists and intellectuals of the time, considered the tower to be an eyesore and unworthy of Paris's aesthetic.
In 1887, Guy de Maupassant joined a group of 300 prominent figures who signed a petition against the tower's construction, arguing that it would ruin the beauty of Paris.
Despite his initial opposition, Guy de Maupassant was later known to dine frequently in the Eiffel Tower's restaurant, claiming it was the only place in Paris where he could avoid seeing the structure he disliked.
Answer:
{{Yes}}, I can answer. The references explicitly state that Guy de Maupassant, a famous French writer, was a vocal critic of the Eiffel Tower during its construction. The references also provide detailed context, including his participation in a petition against the tower and his later ironic behavior of dining in the tower. Therefore, the answer is {{SUPPORTS}}.

# Example 6:
Claim: "The Gadsden flag was named by Christopher Gadsden."
Clues: None
Knowledge Triplets:
(Christopher Gadsden, design, Gadsden flag)
Retrieved References:
Gadsden flag is designed by Christopher Gadsden.
The Gadsden flag is named after politician Christopher Gadsden.
Answer: {{No}}, I can't answer. According to the triples and references, The Gadsden flag is designed by Christopher Gadsden, but there is no information on who named it. There is insufficient evidence to evaluate the claim. Therefore uesful clues so far is {{Gadsden flag is designed by Christopher Gadsden}}.


# Now, please carefully consider the following case:
"""

prompt_reasoning_fever_query_change_3shot_2 = """
# Task: Given a claim, the associated retrieved knowledge triplets and references, you are asked to answer whether the provided references sufficient to verify the claim ({{Yes}} or {{No}}). 
# Note that your answer must begin with {{Yes}} or {{No}}. If you answered {{Yes}}, you must indicate whether the given references SUPPORT or REFUTE the claim, and enclose the result in curly brackets {{SUPPORTS/REFUTES}}. If {No}, it means the resources are useless or provide clues that are helpful but insufficient to answer the question conclusively. Based on the given knowledge, please summarize any insights (if any) so far that may help answer the question, which must also be enclosed in curly brackets{xxxxxx}
# Here are some examples:

# Example 1:
Claim: "Texas is the most populous U.S. state."
Clues: None
Knowledge Triplets:
(Texas, state of, U.S. state)
Retrieved References:
Texas is the second most populous state in the United States, with California being the most populous. 
The population of Texas is approximately 29 million, making it the second most populous state after California.
Answer: {{Yes}}, I can answer. The references explicitly state that Texas is the second most populous state in the United States, with California being the most populous. Therefore, the claim that "Texas is the most populous U.S. state" is incorrect. The answer is {{REFUTES}}.

# Example 2:
Claim: "The Eiffel Tower was initially criticized by the famous French writer Guy de Maupassant."
Clues: None
Knowledge Triplets:
(Eiffel Tower, located in, Paris)
(Guy de Maupassant, occupation, writer)
(Eiffel Tower, located in, Paris)
Retrieved References:
Guy de Maupassant, one of France's most famous writers, was known for his vocal criticism of the Eiffel Tower during its construction. He, along with other artists and intellectuals of the time, considered the tower to be an eyesore and unworthy of Paris's aesthetic.
In 1887, Guy de Maupassant joined a group of 300 prominent figures who signed a petition against the tower's construction, arguing that it would ruin the beauty of Paris.
Despite his initial opposition, Guy de Maupassant was later known to dine frequently in the Eiffel Tower's restaurant, claiming it was the only place in Paris where he could avoid seeing the structure he disliked.
Answer:
{{Yes}}, I can answer. The references explicitly state that Guy de Maupassant, a famous French writer, was a vocal critic of the Eiffel Tower during its construction. The references also provide detailed context, including his participation in a petition against the tower and his later ironic behavior of dining in the tower. Therefore, the answer is {{SUPPORTS}}.

# Example 3:
Claim: "The Gadsden flag was named by Christopher Gadsden."
Clues: None
Knowledge Triplets:
(Christopher Gadsden, design, Gadsden flag)
Retrieved References:
Gadsden flag is designed by Christopher Gadsden.
The Gadsden flag is named after politician Christopher Gadsden.
Answer: {{No}}, I can't answer. According to the triples and references, The Gadsden flag is designed by Christopher Gadsden, but there is no information on who named it. Therefore uesful clues so far is {{The Gadsden flag is designed by Christopher Gadsden}}.
"""

prompt_reasoning_creak_3shot = """
# Task: Given a claim, and supported by your own knowledge along with retrieved knowledge triplets and references (which may or may not be useful), you are tasked to determine whether the claim is {{true}} or {{false}}.
# Note that your answer must begin with {{Yes}} or {{No}}. If you answered {{Yes}}, you must indicate whether the given claim as True/False, and enclose the result in curly brackets {{True/False}}. If you answered {{No}}, indicating you can not answer.
# Here are some examples:

# Example 1:
Claim: "The Great Wall of China is visible from space with the naked eye."
Knowledge Triplets:
(The Great Wall of China, located in, China)
References:
The Great Wall of China, although a massive structure, is not visible to the naked eye from space
The myth that the Great Wall of China is visible from space was debunked
Answer: {{Yes}}, the first sentences explicitly states that the Great Wall is not visible from space with the naked eye. Additionally, the the second sentence confirms that this is a myth and was debunked. The knowledge triplets provide conflicting information, but the references clearly refute the claim. Therefore the answer is {{False}}

# Example 2:
Claim: "Albert Einstein won the Nobel Prize in Chemistry."
Knowledge Triplets:
(Albert Einstein, won, Nobel Prize in Physics)
(Nobel Prize in Chemistry, won by, Marie Curie)
References:
Albert Einstein was awarded the Nobel Prize in Physics in 1921.
Nobel Prize official site: "Marie Curie was awarded the Nobel Prize in Chemistry in 1911.
Answer: {{No}}, the claim that "Albert Einstein won the Nobel Prize in Chemistry" is not provided by the given references. The Wikipedia page states that Einstein won the Nobel Prize in Physics, not Chemistry. The Nobel Prize site mentions Marie Curie as a recipient of the Chemistry prize. There is insufficient evidence to evaluate the claim.

# Example 3:
Claim: "CRISPR technology can be used to edit genes in human embryos."
Knowledge Triplets:
(CRISPR, used in, gene editing)
(CRISPR, edits, human embryos)
(Gene editing, possible in, human embryos)
References:
CRISPR-Cas9 has been successfully used to edit genes in human embryos, raising both hopes for curing genetic diseases and ethical concerns.
Recent experiments have demonstrated the potential of CRISPR to edit genes in human embryos, though the technology is still in its experimental stages and surrounded by ethical debates.
Answer: {{Yes}}, the references explicitly states that CRISPR-Cas9 has been used to edit genes in human embryos, mentioning both the scientific success and the ethical implications. The references also confirms this by discussing recent experiments that have demonstrated the potential of CRISPR for gene editing in human embryos, although it notes that the technology is still experimental. The knowledge triplets align with the claim, and the references provide robust evidence to support it. There the answer is {{True}}

# Now, please carefully consider the following case:
"""

prompt_reasoning_creak_query_change_3shot = """
# Task: Given a claim, and supported by your own knowledge along with retrieved knowledge triplets and references (which may or may not be useful), you are tasked to determine whether the claim is {{true}} or {{false}}.
# Note that your answer must begin with {{Yes}} or {{No}}. If you answered {{Yes}}, you must indicate whether the given claim as True/False, and enclose the result in curly brackets {{True/False}}. If you answered {{No}}, indicating you can not answer, which means your knowledge and the provided information are useless or helpful but insufficient to conclusively judge the claim, identify the missing aspects and refine the search query to specifically target the information needed to complete the answer. The targeted search query also must be enclosed in curly brackets {{xxxxxx}}.
# Here are some examples:

# Example 1:
Claim: "The Great Wall of China is visible from space with the naked eye."
Clues: None
Knowledge Triplets:
(The Great Wall of China, located in, China)
Retrieved References:
The Great Wall of China, although a massive structure, is not visible to the naked eye from space
The myth that the Great Wall of China is visible from space was debunked
Answer: {{Yes}}, the first sentences explicitly states that the Great Wall is not visible from space with the naked eye. Additionally, the the second sentence confirms that this is a myth and was debunked. The knowledge triplets provide conflicting information, but the references clearly refute the claim. Therefore the answer is {{False}}

# Example 2:
Claim: "CRISPR technology can be used to edit genes in human embryos."
Clues: None
Knowledge Triplets:
(CRISPR, used in, gene editing)
(CRISPR, edits, human embryos)
(Gene editing, possible in, human embryos)
Retrieved References:
CRISPR-Cas9 has been successfully used to edit genes in human embryos, raising both hopes for curing genetic diseases and ethical concerns.
Recent experiments have demonstrated the potential of CRISPR to edit genes in human embryos, though the technology is still in its experimental stages and surrounded by ethical debates.
Answer: {{Yes}}, the references explicitly states that CRISPR-Cas9 has been used to edit genes in human embryos, mentioning both the scientific success and the ethical implications. The references also confirms this by discussing recent experiments that have demonstrated the potential of CRISPR for gene editing in human embryos, although it notes that the technology is still experimental. The knowledge triplets align with the claim, and the references provide robust evidence to support it. There the answer is {{True}}

# Example 3:
Claim: "Albert Einstein won the Nobel Prize in Chemistry."
Clues: None
Knowledge Triplets:
(Albert Einstein, won, Nobel Prize in Physics)
(Nobel Prize in Chemistry, won by, Marie Curie)
Retrieved References:
Albert Einstein was awarded the Nobel Prize in Physics in 1921.
Nobel Prize official site: "Marie Curie was awarded the Nobel Prize in Chemistry in 1911.
Answer: {{No}}, the claim that "Albert Einstein won the Nobel Prize in Chemistry" is not provided by the given references. The Wikipedia page states that Einstein won the Nobel Prize in Physics, not Chemistry. The Nobel Prize site mentions Marie Curie as a recipient of the Chemistry prize. There is insufficient evidence to evaluate the claim. Therefore uesful clues so far is {{Einstein won the Nobel Prize in Physics, not Chemistry}}.

# Now, please carefully consider the following case:
"""

prompt_rq = """Given a question and some knowledge gained so far, please predict the additional evidence that
needs to be found to answer the current question, and then provide a suitable query for retrieving
this potential evidence. Note that the output query of yours must be included in curly brackets {{xxx}}.
Question:{}
Knowledge gained so far:{}
Output:"""

query_focus_multi_hop_qa = """
# Given a query, what are the focus questions for these queries?
# You must output as json without any explanation. Here are some examples:
Query: 
What type of vehicle is the Blue Bird Wanderlodge which was manufactured in Georgia by the Blue Bird Corporation?
Output:
{{"Focus_question": "What type of vehicle is the Blue Bird Wanderlodge?"}}

Query: 
What other jobs did the actress Olivia Munn from Mortdecai have?
Output:
{"Focus_question": "What other jobs has Olivia Munn, who starred in Mortdecai, had?"}

Query: 
What number president was Annie Caputo nominated by to become a member of the Nuclear Regulatory Commission?
Output:
{"Focus_question": "Which president nominated Annie Caputo to become a member of the Nuclear Regulatory Commission?"}

Query: 
When did the author of the book One More River is based on win the Nobel Prize?
Output:
{{"Focus_question": "When did the author of the book One More River win the Nobel Prize?"}}

# Now please carefully consider this query:
Query:
"""
