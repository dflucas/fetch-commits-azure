import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.utils.dataframe import dataframe_to_rows
import re
import os
from datetime import datetime

# Função para limpar títulos de abas
def clean_title(title):
    title = str(title)[:31]  # Limita a 31 caracteres
    title = re.sub(r'[\\/*?:"<>|]', '', title)
    return title

# Cria a estrutura de pastas para evidências
def create_evidence_directory():
    current_date = datetime.now().strftime('%Y-%m')
    evidence_dir = os.path.join('evidences', current_date)
    os.makedirs(evidence_dir, exist_ok=True)
    return evidence_dir

# Carregar dados do CSV gerado anteriormente
df = pd.read_csv('commits_by_author_project_and_month.csv')

# Criar uma lista de projetos únicos
projects = df['Project'].unique()

# Criar um novo workbook para salvar os dados e gráficos
workbook = Workbook()

# Adicionar uma aba para os dados
data_sheet = workbook.active
data_sheet.title = 'Dados'

# Escrever os dados no Excel
for r in dataframe_to_rows(df, index=False, header=True):
    data_sheet.append(r)

# Formatação da aba de dados
for column in data_sheet.columns:
    max_length = 0
    column_letter = column[0].column_letter  # Pega a letra da primeira coluna
    for cell in column:
        if cell.value:  # Verifica se a célula não está vazia
            max_length = max(max_length, len(str(cell.value)))
    adjusted_width = (max_length + 2)
    data_sheet.column_dimensions[column_letter].width = adjusted_width

# Criar diretório para as evidências
evidence_directory = create_evidence_directory()

# Loop para criar gráficos e adicioná-los em abas
for project in projects:
    project_clean_title = clean_title(project)  # Limpa o título
    project_dir = os.path.join(evidence_directory, project_clean_title)  # Diretório do projeto
    os.makedirs(project_dir, exist_ok=True)  # Cria o diretório se não existir

    project_df = df[df['Project'] == project]

    # Gráfico de quantidade de commits por autor
    total_commits = project_df.groupby('Author')['Commits'].sum().reset_index()
    total_commits.columns = ['Author', 'Total Commits']

    # Gráfico de distribuição de commits por autor
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Total Commits', y='Author', data=total_commits.sort_values('Total Commits', ascending=False))
    plt.title(f'Distribuição de Commits por Autor - {project}')
    plt.xlabel('Total de Commits')
    plt.ylabel('Autor')
    plt.tight_layout()

    # Salvar o gráfico como PNG
    png_filename = f'{project_clean_title}_commit_distribution.png'
    plt.savefig(os.path.join(project_dir, png_filename))
    plt.close()

    # Gráfico de quantidade de commits por mês
    monthly_trends = project_df.groupby(['Month'])['Commits'].sum().reset_index()
    monthly_trends.columns = ['Month', 'Total Commits']
    monthly_trends['Month'] = pd.to_datetime(monthly_trends['Month'])

    # Gráfico de linha para tendências mensais
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='Month', y='Total Commits', data=monthly_trends, marker='o')
    plt.title(f'Tendência Mensal de Commits - {project}')
    plt.xlabel('Mês')
    plt.ylabel('Total de Commits')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Salvar o gráfico como PNG
    monthly_png_filename = f'{project_clean_title}_monthly_trend.png'
    plt.savefig(os.path.join(project_dir, monthly_png_filename))
    plt.close()

    # Adicionar uma nova aba para cada projeto
    project_sheet = workbook.create_sheet(title=project_clean_title)

    # Adicionar gráficos como imagens nas abas do Excel
    img_dist = Image(os.path.join(project_dir, png_filename))
    project_sheet.add_image(img_dist, 'A1')

    img_trend = Image(os.path.join(project_dir, monthly_png_filename))
    project_sheet.add_image(img_trend, 'A20')  # Adicione o gráfico de tendência abaixo do gráfico anterior

# Salvar o arquivo Excel
xls_filename = 'commit_analysis_report.xlsx'
workbook.save(os.path.join(evidence_directory, xls_filename))

print("Relatório de análise de commits gerado com sucesso!")
