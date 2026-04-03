import json
from datetime import datetime
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

import os

CLOUD_TASKS_QUEUE = os.getenv("CLOUD_TASKS_QUEUE")
CLOUD_TASKS_BASE_URL = os.getenv("CLOUD_TASKS_BASE_URL")    


def schedule_task(url_path: str, payload: dict, schedule_time: datetime) -> None:
    """
    Schedule an HTTP POST Cloud Task at a specific datetime.

    :param url_path:      Path on this service, e.g. "/assignments/check-deadline/42"
    :param payload:       JSON-serialisable dict that will be the request body
    :param schedule_time: UTC datetime when the task should fire
    """
    client = tasks_v2.CloudTasksClient()

    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": f"{CLOUD_TASKS_BASE_URL}{url_path}",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(payload).encode(),
        }
    }

    # Convert datetime → protobuf Timestamp
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(schedule_time)
    task["schedule_time"] = ts

    client.create_task(parent=CLOUD_TASKS_QUEUE, task=task)