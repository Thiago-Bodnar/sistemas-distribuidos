# corridas-distribuidas-api

## Como rodar este projeto

1. Instale o gerenciador [uv](https://github.com/astral-sh/uv):

```bash
pip install uv
```

2. Instale as dependências do projeto:

```bash
uv sync
```

3. Rode o MariaDB com Docker:

```bash
docker run --name mariadb -e MYSQL_ROOT_PASSWORD=mypass -p 3306:3306 -d docker.io/library/mariadb:10.6
```

4. Acesse o MariaDB e crie uma base `fastapi`

```bash
docker exec -it mariadb mariadb -u root -pmypass
```

No console, rode o seguinte:

```sql
CREATE DATABASE fastapi;
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

