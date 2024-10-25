import requests
import pandas as pd
import base64
import re
from datetime import datetime
from collections import defaultdict

# Configurações
organization = ''
project = ''  
repo_id = ''
token = '<YOUR_TOKEN_HERE>'

# Codificando o token em Base64
encoded_token = base64.b64encode(f":{token}".encode()).decode()

# URL base da API para buscar repositórios do projeto
repos_url = f'https://dev.azure.com/{organization}/{project}/_apis/git/repositories?api-version=7.0'

# Headers com autenticação
headers = {
    'Authorization': f'Basic {encoded_token}',
    'Content-Type': 'application/json'
}
# Função para buscar todos os repositórios do projeto
def get_repositories():
    repos = []
    response = requests.get(repos_url, headers=headers)

    if response.status_code == 200:
        repos = response.json().get('value', [])
    else:
        print(f"Erro ao buscar repositórios: {response.status_code} - {response.text}")
    
    return repos

# Função para buscar todos os commits de um repositório com paginação e filtro por data
def get_commits(repo_id):
    commits = []
    base_url = f'https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repo_id}/commits'
    params = {
        'api-version': '7.0',
        '$top': 1000,
        'searchCriteria.fromDate': '2024-01-01T00:00:00Z'  # Buscar a partir de 2024
    }
    
    skip = 0
    while True:
        params['$skip'] = skip  # Adiciona o parâmetro de pular commits

        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                current_commits = data.get('value', [])
                
                # Se não houver mais commits, sai do loop
                if not current_commits:
                    break

                commits.extend(current_commits)

                # Exibe o progresso
                print(f"Buscando commits do repositório {repo_id}, página atual com {len(current_commits)} commits.")

                # Incrementa o valor de skip
                skip += 1000  # Aumenta o número de commits a pular para a próxima requisição
            else:
                print(f"Erro ao buscar commits do repositório {repo_id}: {response.status_code} - {response.text}")
                break
        except requests.exceptions.Timeout:
            print(f"Timeout ao buscar commits para o repositório {repo_id}. Tentando novamente...")
            continue  # Continua a tentativa na próxima iteração
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            break  # Sai do loop em caso de erro inesperado
    
    return commits

# Função para extrair o nome do autor a partir do e-mail
def extract_name_from_email(email):
    # Extrai a parte do nome antes do domínio e substitui "@" por " "
    name_part = email.split('@')[0]
    return name_part.replace('.', ' ')  # Converte nome.sobrenome para nome sobrenome

# Função para identificar o projeto a partir do título do commit
def extract_project_from_title(title):
    # Usando expressões regulares para capturar o padrão .*?-
    match = re.search(r'(XXXXX.*?)-', title)  # Regex para encontrar DSUP seguido de qualquer coisa até o hífen
    if match:
        return match.group(1)  # Retorna o projeto encontrado
    return 'N/A'  # Retorna N/A se não encontrar o projeto

# Função para organizar os commits por autor, projeto e mês
def organize_commits_by_author_project_and_month(commits):
    commit_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for commit in commits:
        email = commit['author']['email']
        author_name = extract_name_from_email(email)  # Extraindo o nome do autor
        date_str = commit['author']['date']
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        month = date.strftime("%Y-%m")
        title = commit['comment']  # O título do commit geralmente está no campo 'comment'
        project = extract_project_from_title(title)  # Extraindo o projeto

        commit_data[author_name][project][month] += 1
    
    return commit_data

# Função para converter o dicionário em DataFrame do Pandas
def convert_to_dataframe(commit_data):
    data = []

    for author, projects in commit_data.items():
        for project, months in projects.items():
            for month, commit_count in months.items():
                data.append({'Author': author, 'Project': project, 'Month': month, 'Commits': commit_count})

    df = pd.DataFrame(data)
    return df

# Função para buscar commits sequencialmente para todos os repositórios
def fetch_commits(repos):
    all_commit_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    # Função auxiliar para cada repositório
    for repo in repos:
        repo_id = repo['id']
        repo_name = repo['name']
        print(f"Buscando commits para o repositório: {repo_name}")
        
        commits = get_commits(repo_id)
        
        if commits:
            commit_data = organize_commits_by_author_project_and_month(commits)
            
            # Combinando os resultados de todos os repositórios
            for author, projects in commit_data.items():
                for project, months in projects.items():
                    for month, count in months.items():
                        all_commit_data[author][project][month] += count

    return all_commit_data

# Função principal
def main():
    repos = get_repositories()  # Certifique-se de que esta função está implementada
    all_commit_data = fetch_commits(repos)

    # Converte todos os dados coletados para um DataFrame
    df = convert_to_dataframe(all_commit_data)

    # Exibir resultado
    print(df)

    # Salvar para CSV
    df.to_csv('commits_by_author_project_and_month.csv', index=False)
    print("Dados salvos em 'commits_by_author_project_and_month.csv'.")

if __name__ == "__main__":
    main()