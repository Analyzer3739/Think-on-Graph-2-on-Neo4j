1、安装ollama https://ollama.com/download

2、ollama run llama3:8b

3、安装cuda12.4

4、conda create -n envname python=12.4
   conda activate envname
   conda install pytorch==2.4.0 -c pytorch -c nvidia
   pip install -r requirements.txt

5、安装Neo4j Desktop，创建并运行一个实例，构建知识图谱

6、按照config/.env.example，创建.env文件,其中apikey需要使用阿里云百炼的apikey