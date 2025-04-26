# Django Atomicserver Example

This repository demonstrates the usage of the django `atomicserver` management command to achieve transactional testing in end-to-end (E2E) tests for a Django application.

It features a simple Todo API backend built with Django and Django REST Framework, and a simple frontend application set up for E2E testing using Playwright.

## Project Structure

```
.
├── api/                  # Django backend application
│   ├── todo_api/         # Django project settings, URLs, etc.
│   ├── tasks/            # Example Django app (Todo tasks)
│   ├── atomicserver/     # Contains the django-atomicserver app
│   ├── manage.py         # Django management script
│   ├── pyproject.toml    # Python dependencies
│   ├── uv.lock           # Lock file for dependencies
│   ├── e2e.Dockerfile    # Dockerfile for E2E testing environment
│   └── ...
├── web/                  # Frontend application (e.g., React, Vue)
│   ├── src/              # Frontend source code
│   ├── tests/            # Playwright E2E tests
│   ├── package.json      # Node.js dependencies
│   ├── playwright.config.ts # Playwright configuration
│   ├── e2e.Dockerfile    # Dockerfile for E2E testing environment
│   └── ...
├── .github/              # GitHub Actions workflows
├── compose.e2e.yaml    # Docker Compose file for running E2E tests
├── LICENSE
└── README.md
```

## `atomicserver`

The core idea demonstrated here is the use of `atomicserver`.

`atomicserver` wraps the entire session in a database transaction. This allows fixtures in the database to be rolled back after, allowing a more deterministic testing workflow. To control the state of the database, we can call

- `/atomic/begin/` to begin an transactional block
- `/atomic/setup/` to setup any fixtures required before the test case to run
- `/atomic/rollback/` to rollback any changed fixtures to the previous checkpoint

This ensures each test starts with a clean database state without needing complex teardown logic.

## Local Development Setup

To run `atomicserver` locally for development.

1.  Clone the repository:
    ```bash
    git clone hanhwanglim/django-atomicserver-example
    cd django-atomicserver-example
    ```
2.  Set up the Backend (API):
    ```bash
    cd api 
    uv sync # ensure you have uv installed
    uv run manage.py migrate
    export CI=true  # or set it conditionally, see below
    uv run manage.py atomicserver
    ```

3.  Run the Frontend E2E tests:
    ```bash
    cd web
    npm install
    npx playwright install --with-deps chromium
    npm run build
    npm run test:e2e
    ```

## Running E2E Tests

The `compose.e2e.yaml` file defines the services needed to run the E2E tests. To run the example E2E test suite

```bash
docker compose -f compose.e2e.yaml up --build --abort-on-container-exit
```

The playwright report will be saved in `./playwright-report`

> [!CAUTION]
> `atomicserver` should be used only in local or testing environments such as in CI. Do not run this in production!

Conditionally setting the application in `settings.py` would ensure that `atomicserver` is not registered in the installed apps.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
