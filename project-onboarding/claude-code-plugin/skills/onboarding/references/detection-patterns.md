# Detection Patterns

## Language Detection

### By File Extension

| Extension | Language |
|-----------|----------|
| .ts, .tsx | TypeScript |
| .js, .jsx | JavaScript |
| .py | Python |
| .rs | Rust |
| .go | Go |
| .java | Java |
| .kt, .kts | Kotlin |
| .rb | Ruby |
| .php | PHP |
| .c, .h | C |
| .cpp, .hpp, .cc | C++ |
| .cs | C# |
| .swift | Swift |
| .dart | Dart |
| .lua | Lua |
| .zig | Zig |
| .ex, .exs | Elixir |
| .erl | Erlang |
| .hs | Haskell |
| .ml, .mli | OCaml |
| .scala | Scala |
| .clj | Clojure |

### By Config File

| File | Language/Tool |
|------|---------------|
| package.json | Node.js |
| tsconfig.json | TypeScript |
| pyproject.toml | Python |
| setup.py | Python (legacy) |
| requirements.txt | Python (pip) |
| Cargo.toml | Rust |
| go.mod | Go |
| pom.xml | Java (Maven) |
| build.gradle | Java (Gradle) |
| Gemfile | Ruby |
| composer.json | PHP |
| CMakeLists.txt | C/C++ |
| Makefile | Make |
| mix.exs | Elixir |
| rebar.config | Erlang |
| cabal.project | Haskell |
| build.sbt | Scala |
| project.clj | Clojure |
| pubspec.yaml | Dart |

## Framework Detection

### JavaScript/TypeScript Frontend

| Dependency | Framework |
|------------|-----------|
| react | React |
| vue | Vue |
| @angular/core | Angular |
| svelte | Svelte |
| solid-js | Solid.js |
| preact | Preact |
| lit | Lit |
| next | Next.js |
| nuxt | Nuxt |
| gatsby | Gatsby |
| @sveltejs/kit | SvelteKit |
| remix | Remix |
| astro | Astro |

### JavaScript/TypeScript Backend

| Dependency | Framework |
|------------|-----------|
| express | Express |
| fastify | Fastify |
| koa | Koa |
| hono | Hono |
| @nestjs/core | NestJS |
| hapi | Hapi |
| restify | Restify |

### Python

| Dependency | Framework |
|------------|-----------|
| django | Django |
| flask | Flask |
| fastapi | FastAPI |
| tornado | Tornado |
| aiohttp | aiohttp |
| sanic | Sanic |
| pyramid | Pyramid |
| starlette | Starlette |

### Rust

| Dependency | Framework |
|------------|-----------|
| actix-web | Actix Web |
| axum | Axum |
| rocket | Rocket |
| warp | Warp |
| tide | Tide |

### Go

| Import | Framework |
|--------|-----------|
| github.com/gin-gonic/gin | Gin |
| github.com/labstack/echo | Echo |
| github.com/gofiber/fiber | Fiber |
| net/http | Standard library |

## Test Framework Detection

### JavaScript/TypeScript

| Dependency | Framework |
|------------|-----------|
| jest | Jest |
| vitest | Vitest |
| mocha | Mocha |
| jasmine | Jasmine |
| ava | AVA |
| tap | Tap |
| @playwright/test | Playwright |
| cypress | Cypress |
| puppeteer | Puppeteer |
| @testing-library/react | React Testing Library |
| @vue/test-utils | Vue Test Utils |

### Python

| Dependency | Framework |
|------------|-----------|
| pytest | pytest |
| unittest | unittest (stdlib) |
| nose2 | nose2 |
| behave | behave (BDD) |
| robot | Robot Framework |

### Rust

- Built-in `#[test]` attribute
- `cargo test` command

## Build System Detection

| File | System |
|------|--------|
| package.json scripts | npm/yarn/pnpm |
| Makefile | make |
| CMakeLists.txt | cmake |
| Cargo.toml | cargo |
| go.mod | go build |
| pom.xml | maven |
| build.gradle | gradle |
| Dockerfile | docker |
| docker-compose.yml | docker compose |
| Vitefile | vite |
| webpack.config.js | webpack |
| rollup.config.js | rollup |
| esbuild.config.js | esbuild |
| turbopack.config.js | turbopack |

## CI/CD Detection

| File | Platform |
|------|----------|
| .github/workflows/*.yml | GitHub Actions |
| .gitlab-ci.yml | GitLab CI |
| .circleci/config.yml | CircleCI |
| Jenkinsfile | Jenkins |
| .travis.yml | Travis CI |
| .drone.yml | Drone CI |
| azure-pipelines.yml | Azure Pipelines |
| bitbucket-pipelines.yml | Bitbucket Pipelines |
| cloudbuild.yaml | Google Cloud Build |
| buildkite.yml | Buildkite |

## Code Style Detection

### Linters

| File | Tool |
|------|------|
| .eslintrc.* | ESLint |
| eslint.config.* | ESLint (flat config) |
| .flake8 | flake8 |
| setup.cfg [flake8] | flake8 |
| pyproject.toml [tool.ruff] | Ruff |
| pyproject.toml [tool.pylint] | Pylint |
| .pylintrc | Pylint |
| rustfmt.toml | rustfmt |
| .rustfmt.toml | rustfmt |
| .clang-format | clang-format |
| .golangci.yml | golangci-lint |
| .rubocop.yml | RuboCop |
| .php-cs-fixer.php | PHP CS Fixer |

### Formatters

| File | Tool |
|------|------|
| .prettierrc | Prettier |
| prettier.config.js | Prettier |
| .editorconfig | EditorConfig |
| .stylelintrc | Stylelint |

### Git Hooks

| File | Tool |
|------|------|
| .husky/pre-commit | Husky |
| .pre-commit-config.yaml | pre-commit |
| .lefthook.yml | Lefthook |

### Commit Conventions

| File/Dependency | Tool |
|-----------------|------|
| commitlint.config.js | Commitlint |
| .commitlintrc | Commitlint |
| conventional-changelog | Conventional Commits |
| standard-version | Standard Version |
| semantic-release | Semantic Release |
| release-please | Release Please |
| .releaserc | Semantic Release |

## Database Detection

| Dependency/Config | Database |
|-------------------|----------|
| pg, postgres, psycopg2 | PostgreSQL |
| mysql, mysql2, pymysql | MySQL |
| sqlite3, better-sqlite3 | SQLite |
| mongodb, mongoose, pymongo | MongoDB |
| redis, ioredis, aioredis | Redis |
| elasticsearch, @elastic/elasticsearch | Elasticsearch |
| prisma | Prisma (ORM) |
| drizzle-orm | Drizzle (ORM) |
| typeorm | TypeORM |
| sequelize | Sequelize |
| sqlalchemy | SQLAlchemy |
| knex | Knex (query builder) |

## Package Manager Detection

| Lock File | Manager |
|-----------|---------|
| package-lock.json | npm |
| yarn.lock | yarn |
| pnpm-lock.yaml | pnpm |
| bun.lockb | bun |
| Pipfile.lock | pipenv |
| poetry.lock | poetry |
| uv.lock | uv |
| Cargo.lock | cargo |
| go.sum | go modules |
| Gemfile.lock | bundler |
| composer.lock | composer |

## Monorepo Detection

| File/Pattern | Tool |
|--------------|------|
| lerna.json | Lerna |
| pnpm-workspace.yaml | pnpm workspaces |
| nx.json | Nx |
| turbo.json | Turborepo |
| rush.json | Rush |
| .yarnrc.yml (workspaces) | Yarn workspaces |
| packages/ | Monorepo (generic) |
| apps/ + packages/ | Monorepo (generic) |

## Container/Deployment Detection

| File | Platform |
|------|----------|
| Dockerfile | Docker |
| docker-compose.yml | Docker Compose |
| k8s/*.yaml | Kubernetes |
| kustomization.yaml | Kustomize |
| helm/ | Helm |
| serverless.yml | Serverless Framework |
| terraform/*.tf | Terraform |
| Pulumi.yaml | Pulumi |
| fly.toml | Fly.io |
| vercel.json | Vercel |
| netlify.toml | Netlify |
| render.yaml | Render |
| railway.json | Railway |
