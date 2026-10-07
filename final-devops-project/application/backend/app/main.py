"""TaskBoard API: explicit migrations, bounded queries and observable failures."""
import time
from collections import Counter

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter as MetricCounter, Histogram, generate_latest
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import get_db
from .models import Task
from .schemas import TaskRead, TaskStatus, TaskWrite

app = FastAPI(title="TaskBoard", version="1.0.0")
requests = MetricCounter("taskboard_http_requests_total", "Requests by route", ["method", "path", "status"])
latency = Histogram("taskboard_http_request_duration_seconds", "Request duration", ["method", "path"])


@app.middleware("http")
async def observe_request(request, call_next):
    started = time.monotonic()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        path = route.path if route else "unmatched"
        if path != "/metrics":
            requests.labels(request.method, path, str(status)).inc()
            latency.labels(request.method, path).observe(time.monotonic() - started)


@app.exception_handler(SQLAlchemyError)
async def database_unavailable(request, exception):
    # Never include a connection string or submitted SQL in a client response.
    return JSONResponse(status_code=503, content={"detail": "Database unavailable. Retry shortly."})


@app.get("/")
def index():
    return {"name": "TaskBoard", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "alive"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db.execute(select(Task.id).limit(1))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database or schema unavailable") from None
    return {"status": "ready"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), headers={"Content-Type": CONTENT_TYPE_LATEST})


@app.get("/api/tasks/stats")
def stats(db: Session = Depends(get_db)):
    counts = Counter(dict(db.execute(select(Task.status, func.count(Task.id)).group_by(Task.status)).all()))
    return {"total": sum(counts.values()), **{status: counts[status] for status in ("todo", "in_progress", "done")}}


@app.get("/api/tasks", response_model=list[TaskRead])
def list_tasks(status: TaskStatus | None = None, limit: int = Query(100, ge=1, le=500),
               offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    query = select(Task).order_by(Task.id.desc()).offset(offset).limit(limit)
    if status:
        query = query.where(Task.status == status)
    return db.scalars(query).all()


def find_task(task_id: int, db: Session):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/api/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return find_task(task_id, db)


@app.post("/api/tasks", response_model=TaskRead, status_code=201)
def create_task(body: TaskWrite, response: Response, db: Session = Depends(get_db)):
    task = Task(**body.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    response.headers["Location"] = f"/api/tasks/{task.id}"
    return task


@app.put("/api/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, body: TaskWrite, db: Session = Depends(get_db)):
    task = find_task(task_id, db)
    for field, value in body.model_dump().items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db.delete(find_task(task_id, db))
    db.commit()
    return Response(status_code=204)
