# Script-RSL
Este script foi desenvolvido para otimizar e automatizar a etapa de triagem de títulos e resumos em Revisões Sistemáticas de Literatura. Ele integra os dados exportados da plataforma Parsifal com o modelo de linguagem Gemini-3.1-Flash-Lite

Instalação de dependências e uso do script:
1. Certifique-se de preparar uma pasta contendo o script e a planilha a ser analisada.
2. Abra um terminal no diretório da pasta.
3. Instale todas as bibliotecas: "pip install google-generativeai pandas xlrd openpyxl".
4. Crie uma chave API gratuita em https://aistudio.google.com/
5. Configure as variáveis do script, inserindo sua chave API, adaptando o prompt, quantidade de artigos analisados por vez, nota de corte, etc.
6. Execute o script: "python ScriptRSL.py"
7. Você pode interromper o script com "CTRL + C" para verificar se a planilha está sendo preenchida corretamente ou para tratar algum erro. Depois rode novamente até o fim.
