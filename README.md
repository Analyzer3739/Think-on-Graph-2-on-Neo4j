1、安装ollama https://ollama.com/download

2、ollama run llama3:8b

3、安装cuda12.4

4、conda create -n envname python=12.4
   conda activate envname
   conda install pytorch==2.4.0 -c pytorch -c nvidia
   pip install -r requirements.txt

5、安装Neo4j Desktop，创建并运行一个实例，构建知识图谱

6、按照config/.env.example，创建.env文件,其中apikey需要使用阿里云百炼的apikey


## Academic Reference

This project implements the Think-on-Graph 2.0 (ToG-2) framework described in the following paper:

> **Think-on-Graph 2.0: Deep and Faithful Large Language Model Reasoning with Knowledge-guided Retrieval Augmented Generation**  
> Shengjie Ma, Chengjin Xu, Xuhui Jiang, Muzhi Li, Huaren Qu, Cehao Yang, Jiaxin Mao, Jian Guo  
> *arXiv preprint arXiv:2407.10805v7*  
> Submitted: July 15, 2024; Revised: February 10, 2025  
> DOI: [10.48550/arXiv.2407.10805](https://doi.org/10.48550/arXiv.2407.10805)