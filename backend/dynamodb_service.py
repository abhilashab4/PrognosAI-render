import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_REGION")
)

table = dynamodb.Table("prognosai-predictions")


def save_prediction(
    domain,
    unit,
    true_rul,
    predicted_rul,
    alert
):

    item = {
        "prediction_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "domain": domain,
        "unit": unit,
        "true_rul": Decimal(str(true_rul)),
        "predicted_rul": Decimal(str(predicted_rul)),
        "alert": alert
    }

    table.put_item(Item=item)

    return item