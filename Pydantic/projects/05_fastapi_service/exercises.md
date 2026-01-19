# Project 5: FastAPI + Pydantic Microservice - Exercises

Complete these exercises to master FastAPI + Pydantic integration.

---

## Exercise 1: Add Subtasks

**Objective**: Extend the task model to support subtasks.

**Requirements**:
- Add `subtasks: list[Subtask]` to `TaskRead`
- Create `SubtaskCreate` and `SubtaskRead` models
- Add endpoints:
  - `POST /tasks/{task_id}/subtasks`
  - `PATCH /tasks/{task_id}/subtasks/{subtask_id}`
  - `DELETE /tasks/{task_id}/subtasks/{subtask_id}`
- Update parent task progress based on subtask completion

**Example**:
```python
class SubtaskRead(BaseSchema):
    id: int
    title: str
    is_completed: bool
    parent_task_id: int

class TaskRead(TaskBase):
    # ... existing fields
    subtasks: list[SubtaskRead] = []

    @computed_field
    @property
    def progress(self) -> float:
        if not self.subtasks:
            return 0.0
        completed = sum(1 for s in self.subtasks if s.is_completed)
        return completed / len(self.subtasks) * 100
```

---

## Exercise 2: Add Comments/Notes

**Objective**: Add a comments system to tasks.

**Requirements**:
- Create `CommentCreate` and `CommentRead` models
- Add endpoints:
  - `POST /tasks/{task_id}/comments`
  - `GET /tasks/{task_id}/comments`
  - `DELETE /tasks/{task_id}/comments/{comment_id}`
- Include author information
- Support markdown in comments

**Models**:
```python
class CommentCreate(BaseSchema):
    content: str = Field(..., min_length=1, max_length=2000)

class CommentRead(BaseSchema):
    id: int
    content: str
    author_email: EmailStr
    created_at: datetime
    updated_at: datetime
```

---

## Exercise 3: Implement Webhooks

**Objective**: Add webhook notifications for task events.

**Requirements**:
- Create webhook registration endpoint
- Send webhooks on:
  - Task created
  - Task completed
  - Task overdue
- Include retry logic
- Add webhook signature verification

**Example**:
```python
class WebhookCreate(BaseSchema):
    url: HttpUrl
    events: list[Literal["task.created", "task.completed", "task.overdue"]]
    secret: str = Field(min_length=32)

class WebhookPayload(BaseSchema):
    event: str
    timestamp: datetime
    data: dict
    signature: str  # HMAC-SHA256
```

---

## Exercise 4: Add File Attachments

**Objective**: Support file attachments on tasks.

**Requirements**:
- Use FastAPI's `UploadFile`
- Store file metadata with Pydantic models
- Add endpoints:
  - `POST /tasks/{task_id}/attachments`
  - `GET /tasks/{task_id}/attachments/{attachment_id}`
  - `DELETE /tasks/{task_id}/attachments/{attachment_id}`
- Validate file types and sizes

**Models**:
```python
class AttachmentRead(BaseSchema):
    id: int
    filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime
    uploaded_by: EmailStr

ALLOWED_TYPES = ["image/png", "image/jpeg", "application/pdf"]
MAX_SIZE_MB = 10
```

---

## Exercise 5: Implement Audit Logging

**Objective**: Add comprehensive audit logging.

**Requirements**:
- Log all mutations (create, update, delete)
- Store in structured format
- Add endpoint to query audit logs
- Include user, timestamp, changes

**Models**:
```python
class AuditLogEntry(BaseSchema):
    id: int
    timestamp: datetime
    user_email: EmailStr
    action: Literal["create", "update", "delete"]
    resource_type: str  # "task", "comment", etc.
    resource_id: int
    changes: dict  # {"field": {"old": x, "new": y}}
    request_id: str

# Endpoint
@app.get("/audit-logs", response_model=PaginatedResponse[AuditLogEntry])
```

---

## Exercise 6: Add Real-time Updates with WebSockets

**Objective**: Implement WebSocket endpoint for real-time task updates.

**Requirements**:
- WebSocket endpoint at `/ws/tasks`
- Broadcast task changes to connected clients
- Support subscriptions to specific tasks
- Handle connection/disconnection gracefully

**Example**:
```python
@app.websocket("/ws/tasks")
async def task_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "subscribe":
                await manager.subscribe(websocket, data["task_id"])
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

## Exercise 7: Implement Caching

**Objective**: Add Redis caching for frequently accessed data.

**Requirements**:
- Cache task details
- Cache statistics
- Implement cache invalidation
- Add cache headers to responses

**Example**:
```python
class CacheSettings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    default_ttl: int = 300  # 5 minutes

@app.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    cache: Cache = Depends(get_cache)
) -> TaskRead:
    # Check cache
    cached = await cache.get(f"task:{task_id}")
    if cached:
        return TaskRead.model_validate_json(cached)

    # Fetch and cache
    task = await db.get_task(task_id)
    await cache.set(f"task:{task_id}", task.model_dump_json())
    return task
```

---

## Exercise 8: Add API Versioning

**Objective**: Implement API versioning.

**Requirements**:
- Support `/v1/` and `/v2/` prefixes
- Different models for different versions
- Version in response headers
- Migration guide in docs

**Example**:
```python
from fastapi import APIRouter

v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")

# V1 - Original
@v1_router.get("/tasks/{task_id}", response_model=TaskReadV1)

# V2 - New fields
@v2_router.get("/tasks/{task_id}", response_model=TaskReadV2)

app.include_router(v1_router)
app.include_router(v2_router)
```

---

## Exercise 9: Implement GraphQL Endpoint

**Objective**: Add a GraphQL endpoint alongside REST.

**Requirements**:
- Use Strawberry or Ariadne
- Reuse Pydantic models as much as possible
- Support queries and mutations
- Add at `/graphql`

**Example**:
```python
import strawberry
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Task:
    id: int
    title: str
    status: str
    # ...

@strawberry.type
class Query:
    @strawberry.field
    def tasks(self) -> list[Task]:
        return [Task.from_pydantic(t) for t in db.get_tasks()]

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
```

---

## Exercise 10: Challenge - Full Production Setup

**Objective**: Make the service production-ready.

**Requirements**:
1. **Configuration**
   - Load from environment
   - Support secrets from files
   - Different configs per environment

2. **Observability**
   - Prometheus metrics endpoint
   - Structured JSON logging
   - Request tracing with correlation IDs
   - Health checks (liveness/readiness)

3. **Security**
   - JWT authentication
   - Rate limiting per user
   - Input sanitization
   - CORS configuration

4. **Performance**
   - Connection pooling
   - Response compression
   - ETags for caching
   - Pagination defaults

5. **Documentation**
   - Complete OpenAPI descriptions
   - Example requests/responses
   - Authentication examples

**Deliverables**:
- `docker-compose.yml` for local development
- `Dockerfile` for production
- `kubernetes/` directory with manifests
- `docs/` with deployment guide

---

## Solutions

Create a `solutions/` directory with your implementations.

**Checklist - Project Completion**:
- [ ] Completed at least 5 exercises
- [ ] All tests pass (`pytest test_api.py -v`)
- [ ] Understand separate Create/Read/Update models
- [ ] Can implement custom exception handlers
- [ ] Comfortable with dependency injection
- [ ] Can add new endpoints with proper validation
- [ ] Understand response_model and serialization

---

## Key Takeaways

1. **Separate Models** for Create/Read/Update operations
2. **response_model** controls serialization and documentation
3. **Depends()** enables clean dependency injection
4. **Path/Query/Body** validation with Pydantic types
5. **Exception Handlers** provide structured error responses
6. **Auto-generated OpenAPI** from Pydantic models
7. **from_attributes=True** enables ORM integration

---

## Congratulations!

You've completed the Pydantic Mastery Learning Path!

See `docs/career_mapping.md` for:
- How each project maps to job requirements
- Portfolio presentation tips
- Freelancing opportunities
- Next steps for continued learning
