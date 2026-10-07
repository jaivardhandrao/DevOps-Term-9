# Three-container networking lab

The Compose file creates exactly three networks:

```text
frontend -- frontend_net
frontend -- application_net -- backend
backend  -- database_net    -- database
```

The backend is attached to `application_net` and `database_net`, as required. The frontend and
database do not share a network, so the frontend cannot connect to the database directly.

## Run the lab

```bash
cp .env.example .env
# Replace the example value in .env with a local throwaway password.
docker compose up -d

docker compose exec frontend wget -qO- http://backend:8080
docker compose exec backend nc -zvw 3 database 3306
docker compose exec frontend sh -c 'getent hosts database || true'
docker network ls --filter name=container-networking

docker compose down -v
rm .env
```

The first check proves frontend-to-backend connectivity. The second proves backend-to-database
connectivity. The third intentionally returns no database address because those two containers are
isolated from one another. My run is captured in [verification.txt](verification.txt).

## Fresh isolated topology evidence

The [7 October raw transcript](../evidence/live-20261007T181301Z.txt) records exactly three new bridge networks, frontend→backend HTTP success, backend→new disposable MySQL TCP 3306 success, backend attachment to two networks, and failed frontend database access by both DNS name and direct IP. This independent safe runner uses a Nginx backend on port 80; the Compose example above continues to use its own backend on port 8080. No existing database, password file, or user container was accessed.
