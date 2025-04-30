# Task Manager

Sistema de gerenciamento de tarefas voltado para empresas da construção civil. O objetivo principal é facilitar o acompanhamento de obras, tarefas e comunicação entre clientes e administradores.

## 🚀 Tecnologias Utilizadas

- Python
- Flask
- MySQL
- HTML
- CSS
- JavaScript

## ⚙️ Funcionalidades

1. 📍 `index.html` (Landing Page)
   - Botão "Acessar Obra" (leva para login)
   - Botão "Gerenciar Obras" (leva para login admin)

2. 🔑 `login.html` (Página Única de Login)
   - Campo de seleção: "Sou Cliente" / "Sou Administrador"
   - Formulário dinâmico (muda conforme o tipo de usuário)

3. 👷 `painel-cliente.html`
   - Visão geral da obra do cliente
   - Cronograma visual
   - Galeria de fotos do andamento
   - Chat com o responsável
   - controle de materiais

4. 🛠️ `painel-admin-obras.html` (Lista de Obras)
   - Cards com todas as obras
   - Filtros por status (andamento, planejada, concluída)
   - Botão "Adicionar Obra"

5. 📊 `painel-admin-obra.html` (Detalhe da Obra)
   - Formulário de atualização diária
   - Upload de fotos/vídeos
   - Controle financeiro
   - Gerenciamento de equipe

## 🎯 Público-alvo

Empresas da área da construção civil que desejam melhorar a organização, comunicação e transparência dos processos com seus clientes.

## 📦 Instalação

> Requisitos:
> - Python 3.x
> - MySQL
> - Virtualenv (opcional, mas recomendado)

```bash
# Clone o repositório
git clone https://github.com/pedrohmsimoes/Projeto-PI-Task-Manager.git

# Crie o ambiente virtual e ative
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure o banco de dados no arquivo .env ou config.py

# Execute a aplicação
python app.py
