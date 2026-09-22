```text
                                                              
                               @@@@                           
                           @@@@@@@@@@@@                       
                         @@@@@@@@@@@@@@@@                     
                        @#        =######@                    
                      #             =######                   
                     @#             .######@                  
                     @#              =#####@@                 
                     @#               #####@@                 
                     #  #@@####=   ########@@                 
                     @  ##@@@@@%##@@@@@@@@@@#                 
                     @  ##@@@##@@@@@@@@@@@@ @                 
                     #  = ###### #@@@@@@@##%@                 
                      #@### ###   #@#######@                  
                                  #########@                  
                     #       ## @@@@@####%@@                  
                     @#     .#@@@@@@#####@@@                  
                     @@# #@@@######@@@@#@@@@                  
                      @# %@########@@@@@@@@                   
                      @@#@#   ######@@@@@@                    
                       @@@@@##@@@@@@@@@@@=                    
                    %   @@@@@###@@@@@@@@@@@##.                
                 @@@     @@@@@@@@@@@@@@@@@@@@@@%=             
             @@@@@@@      .@@@@@@@@@@@@@@@@@@@@@@@@@#         
         @@@@@@@@@@@         ##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  
     @@@@@@@@@@@@@@@@          ###@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  @@@@@@@@@@@@@@@@@@@@@        .##.#@@@@@@@@@@@@@@@@@@@@@@@@@@
 @@@@@@@@@@@@@@@@@@@@@@@@@@###@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
```

# Vivento — Plataforma de Gestão de Eventos

Teste técnico para a vaga de Desenvolvedor(a) Full Stack Pleno — VB Alimentos.

Plataforma simples de gestão de eventos: organizadores criam e gerenciam
eventos, e qualquer pessoa pode se inscrever como participante, respeitando
o limite de vagas de cada evento.

- **Backend**: `event-management-back` — Python + FastAPI + SQLAlchemy + SQLite
- **Frontend**: `event-management-front` — React (Vite) + React Router + Axios

---

## Índice

- [Como rodar localmente](#como-rodar-localmente)
  - [Opção A — com Docker (recomendado)](#opção-a--com-docker-recomendado)
  - [Opção B — sem Docker](#opção-b--sem-docker)
- [Como rodar os testes](#como-rodar-os-testes)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Documentação da API](#documentação-da-api)
- [Decisões de arquitetura](#decisões-de-arquitetura)
- [Cloud native readiness](#cloud-native-readiness)
- [Próximos passos](#próximos-passos-com-mais-tempo)

---

## Como rodar localmente

### Opção A — com Docker (recomendado)

Pré-requisitos: Docker e Docker Compose.

```bash
# Na raiz do projeto
# Lembre-se de utilizar o sudo ou usuário com maior autenticação caso esteja utilizando linux
cp .env.example .env   # opcional — os valores padrão já funcionam localmente
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend (API + docs Swagger): http://localhost:8000/docs
- Health checks: http://localhost:8000/health e http://localhost:3000/health

O `docker-compose.yml` sobe backend e frontend com um único comando, já com
health checks configurados e um volume nomeado (`backend-data`) para
persistir o arquivo SQLite entre reinicializações.

Para derrubar tudo:

```bash
docker compose down          # mantém o volume de dados
docker compose down -v       # remove também o volume (apaga o banco)
```

### Opção B — sem Docker

Pré-requisitos: Python 3.12+, Node.js 20+.

**Backend:**

```bash
cd event-management-back
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

A API sobe em http://localhost:8000 (docs interativas em `/docs`). As
tabelas do SQLite são criadas automaticamente no primeiro start, dentro de
`event-management-back/data/`.

**Frontend** (em outro terminal):

```bash
cd event-management-front
cp .env.example .env    # já aponta para http://localhost:8000
npm install
npm run dev
```

O frontend sobe em http://localhost:5173 e já está configurado (via
`VITE_API_URL`) para conversar com o backend em `localhost:8000`.

---

## Como rodar os testes

**Backend** (pytest, com relatório de cobertura):

```bash
cd event-management-back
source .venv/bin/activate   # se ainda não estiver ativo
pytest
```

26 testes cobrindo autenticação, CRUD de eventos, filtros por status/data e
inscrição de participantes (incluindo o limite de vagas), com ~94% de
cobertura de `app/`.

**Frontend** (lint):

```bash
cd event-management-front
npm run lint
```

O projeto não inclui testes de frontend (ver [Próximos passos](#próximos-passos-com-mais-tempo)).

**Pipeline de CI**: todo push/PR para `main` roda automaticamente lint +
testes + build das imagens Docker de ambos os serviços — veja
`.github/workflows/ci.yml`.

---

## Variáveis de ambiente

Nenhuma configuração sensível ou variável está hardcoded no código — tudo
vem de variáveis de ambiente, com um `.env.example` em cada serviço.

### Backend (`event-management-back/.env.example`)

| Variável                       | Descrição                                              | Padrão (dev)                    |
| ------------------------------- | ------------------------------------------------------ | -------------------------------- |
| `DATABASE_URL`                  | String de conexão (SQLite local ou Postgres em prod)    | `sqlite:///./data/event_management.db` |
| `SECRET_KEY`                    | Chave usada para assinar os tokens JWT                 | *(troque em produção)*           |
| `ALGORITHM`                     | Algoritmo do JWT                                        | `HS256`                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES`   | Expiração do token de acesso                            | `60`                              |
| `CORS_ORIGINS`                  | Origens permitidas (separadas por vírgula)               | `http://localhost:5173,...`      |

### Frontend (`event-management-front/.env.example`)

| Variável        | Descrição                                     | Padrão (dev)            |
| ---------------- | ---------------------------------------------- | ------------------------- |
| `VITE_API_URL`   | URL base da API backend                        | `http://localhost:8000`   |

> **Nota:** o Vite injeta `VITE_*` no bundle estático em **build-time**, não
> em runtime. No Docker, isso é feito via `ARG VITE_API_URL` no
> `Dockerfile` do frontend (repassado pelo `docker-compose.yml`). Se a URL
> da API mudar, é necessário reconstruir a imagem do frontend.

---

## Estrutura do projeto

```
.
├── event-management-back/       # API (FastAPI)
│   ├── app/
│   │   ├── core/config.py       # Settings via variáveis de ambiente
│   │   ├── routers/             # auth, events, participants
│   │   ├── services/            # regras de negócio (status, filtros)
│   │   ├── models.py            # models SQLAlchemy (User, Event, Participant)
│   │   ├── schemas.py           # schemas Pydantic (validação/serialização)
│   │   ├── security.py          # hashing, JWT, OAuth2PasswordBearer
│   │   ├── database.py          # engine/sessão SQLAlchemy
│   │   └── main.py              # app FastAPI, CORS, health check, logging
│   ├── tests/                   # testes pytest (isolados, banco em memória)
│   ├── Dockerfile                # multi-stage, imagem enxuta, non-root
│   └── requirements.txt
│
├── event-management-front/       # SPA (React + Vite)
│   ├── src/
│   │   ├── api/                  # client Axios + chamadas por domínio
│   │   ├── context/AuthContext.jsx
│   │   ├── components/           # Navbar, EventCard, ParticipantsPanel...
│   │   ├── pages/                 # Login, Register, EventsList, EventDetail, EventForm
│   │   └── styles/global.css      # design tokens (cores, tipografia)
│   ├── Dockerfile                 # multi-stage: build Node → serve Nginx
│   └── nginx.conf                 # SPA fallback + health check
│
├── k8s/                           # manifests de exemplo (diferencial)
├── .github/workflows/ci.yml       # pipeline de CI (lint + testes + build)
└── docker-compose.yml             # orquestra os dois serviços localmente
```

---

## Documentação da API

Com o backend rodando, a documentação interativa (Swagger) fica disponível
em **http://localhost:8000/docs** (e o schema OpenAPI em `/openapi.json`).

Principais endpoints:

| Método | Rota                                    | Auth? | Descrição                                  |
| ------ | ---------------------------------------- | ----- | -------------------------------------------- |
| POST   | `/auth/register`                         | não   | Cria um usuário organizador                  |
| POST   | `/auth/token`                            | não   | Login (OAuth2 password flow) → retorna JWT   |
| GET    | `/auth/me`                               | sim   | Dados do usuário autenticado                 |
| GET    | `/events`                                | não   | Lista eventos (filtros `status`, `date`)     |
| POST   | `/events`                                | sim   | Cria evento                                  |
| GET    | `/events/{id}`                           | não   | Detalhe do evento                            |
| PUT    | `/events/{id}`                           | sim*  | Atualiza evento (apenas o organizador)       |
| DELETE | `/events/{id}`                           | sim*  | Remove evento (apenas o organizador)         |
| GET    | `/events/{id}/participants`              | sim*  | Lista participantes do evento                |
| POST   | `/events/{id}/participants`              | não   | Inscreve um participante (respeita vagas)    |
| DELETE | `/events/{id}/participants/{pid}`        | sim*  | Remove participante (apenas o organizador)   |
| GET    | `/health`, `/healthz`                    | não   | Health check                                 |

\* requer ser o organizador (dono) do evento, não apenas estar autenticado.

**Testando autenticação no Swagger UI**: clique em "Authorize", informe
e-mail/senha (criados via `/auth/register`) — o Swagger já usa o fluxo
OAuth2 password corretamente.

---

## Decisões de arquitetura

- **FastAPI + SQLAlchemy 2.0 (typed) + SQLite**: stack moderna, tipada de
  ponta a ponta (Pydantic + SQLAlchemy `Mapped[]`), com documentação OpenAPI
  automática. SQLite atende bem ao escopo do desafio e à persistência local;
  a troca para Postgres é apenas uma mudança de `DATABASE_URL` (nenhum
  código depende de SQLite especificamente).
- **Arquitetura em camadas**: `routers` (HTTP/validação) → `services`
  (regras de negócio, ex: cálculo de status do evento e filtros) → `models`
  (persistência). Isso mantém os endpoints finos e testáveis, e facilita
  trocar a camada de persistência no futuro.
- **Status do evento derivado, não armazenado**: `future`/`past`/`full` é
  calculado em tempo real a partir de `date_time`, `capacity` e da contagem
  de participantes — evita inconsistência entre o dado salvo e a realidade
  (ex: evento marcado como "aberto" mesmo depois de lotar).
- **Autenticação OAuth2 (JWT) via `OAuth2PasswordBearer`**: login separado
  de inscrição em evento. Criar/editar/remover eventos exige estar
  autenticado **e** ser o organizador do evento; já a inscrição de
  participantes é pública (reflete o uso real — quem se inscreve num evento
  não precisa ter conta na plataforma).
- **SQLite em ambiente concorrente**: `check_same_thread: False` é usado
  para permitir o uso do mesmo arquivo entre threads do Uvicorn/TestClient.
  Em um cenário de produção com múltiplas réplicas, a recomendação é migrar
  para Postgres (ver `k8s/README.md`).
- **Frontend com Context API (sem Redux)**: o estado global necessário é só
  a sessão do usuário — `AuthContext` cobre isso sem adicionar uma
  dependência extra. Dados de eventos ficam em estado local de cada página,
  buscados via Axios.
- **Build-time env var no frontend (`VITE_API_URL`)**: Vite não expõe
  variáveis de ambiente em runtime; a URL da API é injetada no build via
  `ARG` do Docker. É uma limitação conhecida de SPAs estáticas servidas por
  Nginx — documentada para o time de infra não ser pego de surpresa.

---

## Cloud native readiness

- **Health checks** (`/health` e `/healthz` no backend, `/health` no
  frontend via Nginx) prontos para liveness/readiness probes.
- **Configuração via env vars** em ambos os serviços — nenhum valor
  sensível ou específico de ambiente hardcoded.
- **Dockerfiles multi-stage**, imagens finais enxutas (`python:3.12-slim` e
  `nginx:1.27-alpine`), rodando com usuário não-root quando possível.
- **Logs estruturados** (JSON-like) via `logging`, indo para stdout — padrão
  esperado por coletores de log em Kubernetes.
- **Stateless quando possível**: o frontend é totalmente stateless. O
  backend só tem estado por causa do arquivo SQLite — ver observações e
  caminho de migração para Postgres em `k8s/README.md`.
- Manifests de exemplo (`k8s/`) com Deployment, Service, ConfigMap/Secret e
  probes configuradas, como referência para o time de infraestrutura.

---

## Próximos passos (com mais tempo)

- **Migrations com Alembic**: hoje as tabelas são criadas via
  `Base.metadata.create_all` no startup, o que é aceitável para SQLite num
  desafio, mas não é o caminho correto para evolução de schema em produção.
- **Migrar para Postgres em produção** e permitir múltiplas réplicas do
  backend com segurança (o `k8s/README.md` já documenta esse caminho).
- **Testes de frontend** (Vitest + Testing Library) para os fluxos
  principais (login, criação de evento, inscrição).
- **Testes E2E** (Playwright/Cypress) cobrindo o fluxo completo
  organizador → cria evento → participante se inscreve.
- **Observabilidade**: métricas Prometheus (`/metrics`), tracing distribuído
  (OpenTelemetry) e correlação de logs por `request_id`.
- **Rate limiting** no endpoint público de inscrição de participantes, para
  mitigar abuso.
- **Paginação** na listagem de eventos e de participantes (hoje retorna
  tudo de uma vez — ok para o volume esperado no desafio).
- **Refresh tokens** e expiração mais curta do access token, hoje o token
  dura 60 minutos sem renovação automática.
- **CI mais completo**: publicar as imagens Docker em um registry
  (ex: GHCR) a cada merge em `main`, com tags por SHA, e um job de deploy
  automatizado para o cluster.
- **Ingress + TLS** nos manifests Kubernetes, hoje deixados de fora por
  dependerem do controller disponível no cluster de destino.
