# Assignment Microservice

A FastAPI microservice for managing assignments, backed by **Google Firestore** and using the **Outbox Pattern** for reliable Pub/Sub event publishing.

---

## Folder Structure

```
assignment_service/
├── main.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── app/
    ├── api/
    │   ├── assignment_controller.py   # REST endpoints for assignments
    │   └── outbox_controller.py       # REST endpoint for outbox/pub-sub
    ├── core/
    │   ├── config.py                  # Settings via pydantic-settings
    │   └── firestore_client.py        # Firestore singleton client
    ├── dtos/
    │   ├── assignment_dto.py          # Request/response DTOs
    │   └── outbox_dto.py
    ├── helpers/
    │   ├── datetime_helpers.py        # UTC utilities
    │   └── pubsub_helper.py           # Pub/Sub publisher
    ├── models/
    │   ├── assignment.py              # Assignment Firestore model
    │   ├── outbox.py                  # Outbox Firestore model
    │   └── other_event.py             # OtherEvent idempotency model
    ├── repository/
    │   ├── assignment_repository.py   # Firestore CRUD for assignments
    │   ├── outbox_repository.py       # Firestore CRUD for outbox
    │   └── other_event_repository.py  # Firestore CRUD for other_events
    └── service/
        ├── assignment_service.py      # Business logic + outbox writes
        └── outbox_service.py          # Pub/Sub publishing logic
```

---

## Firestore Collections

| Collection      | Purpose                                           |
|-----------------|---------------------------------------------------|
| `assignments`   | Core assignment documents                         |
| `outbox`        | Reliable event queue for Pub/Sub (outbox pattern) |
| `other_events`  | Tracks handled external events (idempotency)      |

---

## API Endpoints

### Assignments — `POST /assignments`
| Method   | Path                             | Description                                  |
|----------|----------------------------------|----------------------------------------------|
| `POST`   | `/assignments/`                  | Create a new assignment                      |
| `GET`    | `/assignments/`                  | List all assignments                         |
| `PATCH`  | `/assignments/{id}`              | Edit an existing assignment                  |
| `DELETE` | `/assignments/{id}`              | Delete an assignment                         |
| `GET`    | `/assignments/deadline-reached`  | Assignments past their submission deadline   |
| `GET`    | `/assignments/leaderboard`       | Leaderboard ranked by submission count       |

### Outbox — `POST /outbox`
| Method | Path                    | Description                                  |
|--------|-------------------------|----------------------------------------------|
| `POST` | `/outbox/pending-events`| Publish all pending outbox events to Pub/Sub |

---

## Setup

```bash
cp .env.example .env
# Fill in PROJECT_ID and PUBSUB_TOPIC

pip install -r requirements.txt
uvicorn main:app --reload
```

### Docker

```bash
docker build -t assignment-service .
docker run -p 8000:8000 --env-file .env assignment-service
```

Interactive docs: `http://localhost:8000/docs`

---

## Outbox Pattern

Every mutation (create / edit / delete) writes a Firestore document to the `outbox` collection with `pending: true`.  
Calling `POST /outbox/pending-events` fetches all pending events, publishes them to Pub/Sub, and marks them as `pending: false`.  
This can be triggered by a Cloud Scheduler job or an internal cron.

---

## Idempotency

The `other_events` collection stores `event_id` strings for every external event that has already been processed. Before handling any incoming event, check `OtherEventRepository.exists(event_id)`.
