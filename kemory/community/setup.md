# Setup

Kemory Community Edition is installed through npm. v0.1 supports the Docker
runtime and reserves the local ports below.

- `docker` - default and recommended for local development and QA.
- `local` - writes host-local configuration only; binary packaging is deferred.

Docker is the default path for local development, QA, and the first community
release.

## Docker Runtime

```bash
npx kemory-community@latest init --runtime docker
npx kemory-community@latest up
npx kemory-community@latest doctor
npx kemory-community@latest bundle
```

The Docker runtime uses the local port registry allocation:

| Service | Host | Container |
| --- | ---: | ---: |
| API | `8111` | `8000` |
| Dashboard | `5175` | `5173` |
| Postgres + pgvector | `5434` | `5432` |

The API will be available at `http://127.0.0.1:8111` and the dashboard at
`http://127.0.0.1:5175`.

The bundle command prints the exact components used by the selected profile.
The standalone profile includes the API, dashboard, PostgreSQL with pgvector,
Redis, in-process FastEmbed, direct Community LLM adapters, and local artifact
storage. Leaving cloud provider keys empty keeps those paths offline.

## Language Model Setup

Open `http://127.0.0.1:5175/settings`, then use **Runtime > Language model**
to select Groq, llama.cpp, or Vertex AI. Enter the provider settings, run
**Test connection**, and save. Credentials are stored in the mode-`0600`
Community configuration file on the API data volume and are never returned by
the settings API.

| Provider | Required settings | Default endpoint |
| --- | --- | --- |
| llama.cpp | Model and an endpoint reachable from the API container; bearer token is optional | `http://host.docker.internal:8080` |
| Groq | Model and Groq API key | `https://api.groq.com/openai` |
| Vertex AI | Gemini model and Vertex AI Express API key | Managed by the Google Gen AI SDK |

The supplied Compose files map `host.docker.internal` on Linux and Docker
Desktop. For llama.cpp running as another container on the same network, use
its service URL, such as `http://llama-cpp:8080`. This endpoint is user-managed
and is not a Kemory-published host port, so it adds no Kemory port-registry
allocation.

Headless deployments can set the same values before startup:

```bash
KEMORY_LLM_PROVIDER=llama_cpp
KEMORY_LLM_MODEL=local-model
KEMORY_LLM_BASE_URL=http://host.docker.internal:8080
KEMORY_LLM_API_KEY=
```

Provider-specific `GROQ_API_KEY`, `GROQ_BASE_URL`, `GOOGLE_API_KEY`, and
`LLAMA_CPP_API_KEY` variables remain supported.

## SeKondBrain Shared Infrastructure

On a host with the canonical shared stack, initialize and provision an isolated
database/user plus Redis logical database before starting the application
containers:

```bash
npx kemory-community@latest init --runtime docker --infra shared
npx kemory-community@latest provision-shared
npx kemory-community@latest up
```

The Community API remains on `8111` and dashboard on `5175`. PostgreSQL reuses
shared port `5432` with database/user `kemory_community`; Redis reuses `6379`
with logical database `14`. New optional profiles must reserve published ports
in the central infra registry before deployment.

## Bundle Boundaries

Core AI Backend and Core Backend are not runtime prerequisites for Community.
The former is Kora's broader hosted cognition service; Community already uses
embedded FastEmbed and direct provider adapters. The latter is the hosted
organization and identity system of record; Community uses one local API key
and local filesystem artifacts.

Keycloak is likewise not started by the default bundle. It remains a future
optional profile, gated on an approved multi-user isolation design, idempotent
realm/client bootstrap, PKCE/token validation coverage, a registered port, and
local-single-user regression tests. No private repository may enter the public
bundle until redistribution, versioned-image, contract, and Docker acceptance
gates are complete.

## Local Runtime

```bash
npx kemory-community@latest init --runtime local
```

The local runtime writes configuration only. It is useful for inspecting the
generated settings, but it does not start services in v0.1.
