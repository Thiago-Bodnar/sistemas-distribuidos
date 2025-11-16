# corridas-distribuidas-api

## Como rodar este projeto

1. Instale o gerenciador [uv](https://github.com/astral-sh/uv):

```bash
pip install uv
```

2. Instale as dependências do projeto:

```bash
uv add -r requirements.txt

uv sync
```

3. Rode o MariaDB com Docker:

```bash
docker run --name mariadb -e MYSQL_ROOT_PASSWORD=mypass -p 3306:3306 -d docker.io/library/mariadb:10.6
```

4. Acesse o MariaDB e crie uma base `fastapi` e o usuário:

```bash
docker run \                                                        
--name mariadb \
-e MYSQL_ROOT_PASSWORD=mypass \
-p 3306:3306 \
-v mariadb_data:/var/lib/mysql \
-d docker.io/library/mariadb:10.6
```

No console, rode o seguinte:

```sql
CREATE DATABASE fastapi;
CREATE USER 'fastapi'@'%' IDENTIFIED BY 'super-senha';
GRANT ALL PRIVILEGES ON fastapi.* TO 'fastapi'@'%';
FLUSH PRIVILEGES;
```

5. Rode as migrations:

```bash
 uv run alembic revision --autogenerate -m "Cria as tabelas iniciais"
 ``` 

6. Rode a aplicação FastAPI:

```bash
uv run fastapi dev
```

Pronto! A aplicação estará rodando.

