#É necessário ter uma conta na Google Cloud e acesso à API Gemini para rodar este script. Lembre-se de configurar o ambiente e instalar as bibliotecas necessárias (google-generativeai, pandas, xlrd) antes de executar.
import google.generativeai as genai
import pandas as pd
import time
import json

API_KEY = "SUA_API_KEY_AQUI"
FILE_INPUT = "articles.xls" #Tabela exportada do parsifal, lembre-se de utilizar o mesmo nome do arquivo.
FILE_OUTPUT = "artigos_analisados.xlsx" #Saída em formato moderno.
MODEL_NAME = 'gemini-3.1-flash-lite'
BATCH_SIZE = 10 #Artigos analisados por vez (ajuste conforme necessário para balancear custo e desempenho. Se puder, use o menor possível). 
                #O modelo utilizado tem um limite de 500 requisições por dia, ou seja: total_artigos / BATCH_SIZE <= 500 para não ultrapassar o limite diário.

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

#Construa o prompt conforme suas necessidades e perguntas específicas. Seja claro e detalhado para obter respostas precisas. O modelo é sensível à qualidade do prompt.
#Exemplo de prompt para análise de artigos sobre Gestão do Conhecimento na Administração Pública, focando em barreiras e facilitadores sob a perspectiva interna.
def build_prompt(chunk):
    prompt = """Você é um revisor acadêmico extremamente rigoroso realizando uma triagem para Revisão Sistemática de Literatura (RSL).
Sua missão é analisar artigos sobre Gestão do Conhecimento na Administração Pública e responder 'Sim' ou 'Não' para 12 perguntas fundamentadas estritamente no texto fornecido.

[CONTEXTO E DIRETRIZES]
O foco deste estudo são as barreiras e facilitadores para as práticas de gestão do conhecimento sob a perspectiva INTERNA da administração pública.
Para responder 'Sim' na Q1, a Gestão do Conhecimento DEVE ser o objeto central de estudo, a lente teórica principal ou uma variável explicitamente investigada (ex: criação, compartilhamento, retenção ou armazenamento do conhecimento organizacional). 
- NÃO marque 'Sim' se o artigo usar as palavras 'gestão' e 'conhecimento' de forma casual, separada ou puramente semântica (ex: 'gestão de contratos requer conhecimento técnico').
- NÃO marque 'Sim' se o foco for apenas gestão de sistemas de informação (TI), gestão de competências ou RH tradicional, a menos que estejam explicitamente integrados a um framework de GC.
- Se o artigo NÃO tiver a GC como foco central, responda 'Não' para todas as perguntas.

- INCLUA: Estudos com uma perspectiva interna da administração pública voltados às rotinas organizacionais, fluxos processuais ou procedimentos administrativos intraorganizacionais (atividade-meio, atos de expediente, gestão de pessoal/servidores/funcionários ou dinâmica burocrática interna).
- EXCLUA OBRIGATORIAMENTE: Estudos com perspectiva externa da Administração Pública (prestação de serviços diretos ao cidadão, formulação/execução de políticas públicas finalísticas, interação direta Estado-sociedade, governo eletrônico ou parcerias entre instituições públicas ou públicas e privadas). Se o artigo for de perspectiva externa, marque 'Não' para as perguntas principais.

[INSTRUÇÕES DE PREENCHIMENTO]
- Só responda 'Sim' se houver evidência textual clara e direta no resumo.
- Na menor dúvida, ambiguidade ou falta de informação, responda 'Não'. Não infira intenções.

Perguntas:
Q1 - Trata de Gestão do conhecimento ou práticas de gestão do conhecimento?
Q2 - Aborda conhecimento tácito?
Q3 - Aborda conhecimento explícito?
Q4 - Estuda barreiras, dificuldades, obstáculos ou resistências na gestão do conhecimento?
Q5 - Estuda barreiras, dificuldades, obstáculos ou resistências individuais ou humanas na gestão do conhecimento?
Q6 - Estuda barreiras, dificuldades, obstáculos ou resistências organizacionais na gestão do conhecimento?
Q7 - Estuda barreiras, dificuldades, obstáculos ou resistências na criação do conhecimento?
Q8 - Estuda barreiras, dificuldades, obstáculos ou resistências no compartilhamento do conhecimento?
Q9 - Estuda facilitadores, promotores ou habilitadores na gestão conhecimento?
Q10 - Estuda facilitadores, promotores ou habilitadores do conhecimento?
Q11 - Estuda facilitadores, promotores ou habilitadores para criação de conhecimento?
Q12 - Estuda facilitadores, promotores ou habilitadores para o compartilhamento do conhecimento?

Responda APENAS em formato JSON (uma lista de objetos) seguindo este modelo exato. É obrigatório preencher a 'justificativa_analise' ANTES de definir as respostas:
[
  {
    "id": "index_do_artigo",
    "justificativa_analise": "Explique brevemente em uma frase se o artigo realmente trata de GC sob a perspectiva interna da administração pública e se apresenta barreiras/facilitadores.",
    "respostas": {
      "Q1": "Sim/Não",
      "Q2": "Sim/Não",
      "Q3": "Sim/Não",
      "Q4": "Sim/Não",
      "Q5": "Sim/Não",
      "Q6": "Sim/Não",
      "Q7": "Sim/Não",
      "Q8": "Sim/Não",
      "Q9": "Sim/Não",
      "Q10": "Sim/Não",
      "Q11": "Sim/Não",
      "Q12": "Sim/Não"
    }
  }
]

Artigos para análise:\n"""
    
    for idx, row in chunk.iterrows():
        t = str(row.get('title', 'N/A'))
        a = str(row.get('abstract', 'N/A'))
        prompt += f"\nID: {idx}\nTítulo: {t}\nResumo: {a}\n"
    return prompt

print(f"Lendo arquivo {FILE_INPUT}...")
try:
    df = pd.read_excel(FILE_INPUT)
except:
    df = pd.read_excel(FILE_INPUT, engine='xlrd')

df_todo = df.reset_index()
total_artigos = len(df_todo)
resultados_acumulados = []


print(f"Iniciando análise de {total_artigos} artigos...")


for i in range(0, total_artigos, BATCH_SIZE):
    chunk = df_todo.iloc[i : i + BATCH_SIZE]
    try:
        response = model.generate_content(build_prompt(chunk))
        
        txt = response.text.strip()
        if "```json" in txt:
            txt = txt.split("```json")[1].split("```")[0].strip()
        elif "```" in txt:
            txt = txt.split("```")[1].split("```")[0].strip()
            
        data = json.loads(txt)
        
        for item in data:
            original_idx = int(item['id'])
            respostas = item['respostas']
            
            sim_count = list(respostas.values()).count("Sim")
            
            row_data = df.iloc[original_idx].to_dict()
            row_data.update(respostas)
            row_data['Score'] = sim_count
            
            #Nota de corte para aprovação, ajuste conforme necessário. 
            if sim_count >= 5:
                row_data['Status_RSL'] = "aprovado"
            else:
                row_data['Status_RSL'] = "reprovado"
                
            resultados_acumulados.append(row_data)
        
        print(f"Processados: {min(i + BATCH_SIZE, total_artigos)}/{total_artigos}")
        
        # Salvar progresso parcial para segurança
        pd.DataFrame(resultados_acumulados).to_excel(FILE_OUTPUT, index=False)
            
        time.sleep(8) #Tempo de espera entre requisições para evitar atingir limites de taxa.

    except Exception as e:
        print(f"Erro no lote {i}: {e}. Tentando novamente em 15s...")
        time.sleep(15)

#Salvamento Final
df_final = pd.DataFrame(resultados_acumulados)
df_final.to_excel(FILE_OUTPUT, index=False)
print(f"Triagem concluída! Arquivo salvo como: {FILE_OUTPUT}")