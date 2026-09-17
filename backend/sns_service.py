import os
import boto3
from dotenv import load_dotenv

load_dotenv()

sns = boto3.client(
    "sns",
    region_name=os.getenv("AWS_REGION")
)

TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")


def send_critical_alert(domain, critical_predictions):

    lines = [
        "CRITICAL MAINTENANCE ALERT",
        "",
        f"Domain: {domain}",
        "",
        "The following units have predicted RUL ≤ 10:",
        ""
    ]

    for item in critical_predictions:
        lines.append(
            f"Unit {item['unit']}\n"
            f"Predicted RUL: {item['predicted_rul']:.2f}\n"
        )

    lines.append(
        f"Total Critical Units: {len(critical_predictions)}"
    )

    message = "\n".join(lines)

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject=f"PrognosAI Critical Maintenance Alert - {domain}",
        Message=message
    )