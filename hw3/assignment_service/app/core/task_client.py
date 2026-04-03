import json
from datetime import datetime
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

import os

CLOUD_TASKS_QUEUE = "taskq"
CLOUD_TASKS_BASE_URL = "https://assignments-service-1088240463128.europe-west1.run.app"  


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
            "oidc_token": {
                "service_account_email": "1088240463128-compute@developer.gserviceaccount.com",
            },
        }
    }

    # Convert datetime → protobuf Timestamp
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(schedule_time)
    task["schedule_time"] = ts

    parent = client.queue_path("cloudcomputing-491711", "europe-west1", CLOUD_TASKS_QUEUE)
    client.create_task(parent=parent, task=task)
