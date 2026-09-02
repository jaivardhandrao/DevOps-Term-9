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
