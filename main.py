import requests  # Biblioteca para chamadas HTTP na API
import requests_cache  # Biblioteca para cache de requisições, melhora performance e reduz chamadas repetidas
import json      # Biblioteca para manipular arquivos JSON
import csv       # Biblioteca para manipular arquivos CSV
import os        # Biblioteca para interagir com o sistema
import sys       # Biblioteca para encerrar o programa com códigos de erro
import argparse  # Biblioteca para tratar argumentos de linha de comando

# adicionei pois enquanto estava fazendo testes recebi um FORBBIDEN/Bloqueio pelo GitHub por excesso de requisições
requests_cache.install_cache('github_cache', expire_after=28800)

# CLASSE 1: O MODELO (ENTIDADE)
# Representa um repositório vindo da API somente com os dados necessarios
class Repository:
    # Constructor - # Armazena somente as informações obrigatorias do repositório que vem do from_api
    def __init__(self, name, full_name, html_url, language, stars, forks, updated_at):
        self.name = name
        self.full_name = full_name
        self.html_url = html_url
        self.language = language if language else "Desconhecida"
        self.stargazers_count = stars
        self.forks_count = forks
        self.updated_at = updated_at

    @classmethod
    def from_api(cls, data: dict):
        # Extractor - Cria um objeto Repository extraindo só os dados importantes que vem do GitHubClient
        # return para o __init__
        return cls(
            name=data.get("name"),
            full_name=data.get("full_name"),
            html_url=data.get("html_url"),
            language=data.get("language"),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            updated_at=data.get("updated_at")
        )

# CLASSE 2: O CLIENTE DA API - Coleta os dados
class GitHubClient:
    #Responsável por fazer requisição HTTP na API.
    def get_repos(self, username: str) -> list[Repository]:
        url = f"https://api.github.com/users/{username}/repos"
        try:
            response = requests.get(url)

            # Verifica se a resposta veio do cache comentei para não aparecer na saida
            is_from_cache = getattr(response, 'from_cache', False)
            if is_from_cache:
                print(f"DEBUG: Dados de '{username}' foram carregados do cache local.")
            
            # Tratamento de erro: usuário inexistente (404)
            if response.status_code == 404:
                raise Exception(f"usuário inexistente (404)")
            
            # Tratamento de erro: limite de requisições (403)
            if response.status_code == 403:
                raise Exception("limite de requisições (403)")
            
            # Lança erro para falhas gerais de rede
            response.raise_for_status() 
            
            data = response.json()
            return [Repository.from_api(repo) for repo in data] # Organiza dados em objetos (List Comprehension)
            
        except requests.exceptions.ConnectionError:
            raise Exception("falha de conexão") # Falha de internet
        except Exception as e:
            raise e

# CLASSE 3: O SERVIÇO DE RELATÓRIO
class ReportService:
    # Responsável por transformar uma lista de Repository em um relatório.
    def gerar_resumo(self, repos: list[Repository]):
        # Calcula métricas básicas: total de repos e total de estrelas
        total_repos = len(repos)
        total_stars = sum(r.stargazers_count for r in repos)
        
        # Identifica os top 5 repositórios por estrelas
        top_5 = sorted(repos, key=lambda r: r.stargazers_count, reverse=True)[:5]
        
        # Contagem por linguagem
        linguagens = {}
        for r in repos:
            linguagens[r.language] = linguagens.get(r.language, 0) + 1
            
        return {
            "total_repos": total_repos,
            "total_stars": total_stars,
            "top_5": top_5,
            "linguagens": linguagens
        }

# CLASSE 4: O ARMAZENAMENTO
class FileStorage:
    # Responsável por salvar dados no disco.
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self._preparar_diretorio()

    def _preparar_diretorio(self):
        # Trata erro de diretório inválido/sem permissão.
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
            except PermissionError:
                raise Exception(f"diretório inválido/sem permissão")

    def salvar(self, username: str, repos: list[Repository], resumo: dict):
        json_path = os.path.join(self.output_dir, f"repos_{username}.json") # Salva JSON
        csv_path = os.path.join(self.output_dir, f"report_{username}.csv")  # Salva CSV

        # Salva a lista normalizada em JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump([r.__dict__ for r in repos], f, indent=4, ensure_ascii=False)

        # Salva o resumo do relatório em CSV
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Métrica", "Valor"])
            writer.writerow(["Total de Repos", resumo["total_repos"]])
            writer.writerow(["Total de Estrelas", resumo["total_stars"]])
            writer.writerow([])
            
            writer.writerow(["Linguagem", "Quantidade"])
            for lang, qtd in resumo["linguagens"].items():
                writer.writerow([lang, qtd])
            writer.writerow([]) # Linha em branco

            writer.writerow(["Top 5 Repositórios", "Estrelas"])
            for repo in resumo["top_5"]:
                writer.writerow([repo.name, repo.stargazers_count])

# PRINCIPAL
if __name__ == "__main__":
    # Configura os argumentos via CLI, mas não é obrigatório para permitir o input depois
    parser = argparse.ArgumentParser(description="Coletor de Dados de uma API Pública")
    parser.add_argument("--username", help="Username do GitHub")
    parser.add_argument("--out", help="Caminho para o diretório de saída")
    args = parser.parse_args()

    # Lógica híbrida: Se não veio por argumento, pede por input
    username = args.username if args.username else input("Digite o username do GitHub: ")
    output_dir = args.out if args.out else input("Digite o diretório de saída (ex: ./output): ")

    try:
        # Inicia serviços (instanciando a Classe)
        client = GitHubClient()
        storage = FileStorage(output_dir)
        service = ReportService()

        # Processamento
        lista_repos = client.get_repos(username)
        resumo = service.gerar_resumo(lista_repos)
        storage.salvar(username, lista_repos, resumo)

        # Saída no terminal como o exemplo exigido
        print(f"\nColetados: {resumo['total_repos']} repositórios")
        print(f"Relatório gerado com total de estrelas: {resumo['total_stars']}")
        print(f"Arquivos salvos em: {output_dir}/…")
        print(f"Arquivos gerados:")
        print(f"./{output_dir}/repos_{username}.json")
        print(f"./{output_dir}/report_{username}.csv")

    # Informa o erro ao usuário
    except Exception as e:
        print(f"Erro: {e}")  
        sys.exit(1)

