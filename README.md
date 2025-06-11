# Projeto API de Gerenciamento com SQLModel

## Dupla:
Janaina Macário de Sousa - Matrícula: 542086
Jamille Bezerra Candido - Matrícula: 

## Descrição

Este projeto é uma API RESTful desenvolvida com FastAPI para gerenciar entidades de um domínio específico usando Mapeamento Objeto-Relacional (ORM) com SQLModel e SQLAlchemy. O banco de dados utilizado foi o PostgreSQL.

A API oferece funcionalidades completas de CRUD, suporte à paginação, filtros, migrações com Alembic e logging para monitoramento das operações.

---

## Funcionalidades

- Criar, ler, atualizar e excluir registros de entidades
- Listagem paginada e filtrada de registros
- Contagem total de registros
- Migrações controladas do banco com Alembic
- Logs para monitoramento de operações

---

## Tecnologias Utilizadas

- Python 3.10+
- FastAPI
- SQLModel / SQLAlchemy
- Alembic
- Banco de dados relacional (PostgreSQL)
- Pydantic para validação de dados

---

## Como Rodar

1. Clone o repositório  
2. Configure as variáveis de ambiente no arquivo `.env`  
3. Instale as dependências com `pip install -r requirements.txt`  
4. Execute as migrações com `alembic upgrade head`  
5. Inicie a API com:

```bash
uvicorn main:app --reload
