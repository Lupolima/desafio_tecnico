# Coletor de Dados API

Projeto desenvolvido como desafio técnico. Esta aplicação conecta na API pública do GitHub, coleta informações sobre os repositórios de um usuário e gera relatórios locais.

## Funcionalidades
1. **Coleta de Dados**: Consome a REST API do GitHub para buscar repositórios de qualquer usuário.
2. **Relatório**: Calcula total de repositórios, total de estrelas, contagem por linguagem e os 5 maiores repositórios
3. **Persistência**: Salva os dados em disco em JSON e o resumo em CSV.
4. **Otimização**: Utiliza cache local para evitar o consumo excessivo da cota da API (Rate Limit)

## Tecnologias
- Python 3.13+
- Biblioteca `requests` (HTTP)
- Biblioteca requests-cache para persistência temporária de requisições.
- Bibliotecas 'JASON' e 'CSV' para salvar no disco

## Como Instalar dependências

1. Certifique-se de ter o Python3 instalado.
2. Instale as dependências listadas no arquivo 'requirements.txt':

   pip install -r requirements.txt

##  Como executar
Opção 1: Via argumentos
Execute o script passando o usuário e a pasta de destino diretamente no terminal:
python main.py --username torvalds --out ./output

Opção 2: Via Input
Basta executar o script sem argumentos:
python main.py


## Quais arquivos são gerados
repos_<username>.json: Lista completa e normalizada de todos os repositórios coletados.

report_<username>.csv: Resumo do relatório e estatísticas por linguagem.
