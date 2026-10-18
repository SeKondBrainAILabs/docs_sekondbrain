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
Redis, in-process FastEmbed, and local artifact storage. Groq synthesis is an
optional direct user-key integration; leaving its key empty keeps that path
offline.

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
