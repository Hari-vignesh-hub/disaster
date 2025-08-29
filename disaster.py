import json
import boto3
import uuid

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')

# Replace with your SNS Topic ARN
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:560836574097:DisasterAlerts"
def send_alert(severity, message):
    """Send SNS alert if disaster severity is High"""
    if severity == "High":
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="🚨 Emergency Alert!"
        )
        return response

def lambda_handler(event, context):
    try:
        # Determine if the event came from API Gateway or direct test
        if 'body' in event:
            report = json.loads(event['body'])
        else:
            report = event

        # Severity determination logic
        severity = "Low"
        if report.get("magnitude", 0) >= 6.0 or report.get("flood_level", 0) > 80:
            severity = "High"
        elif report.get("magnitude", 0) >= 4.0 or report.get("flood_level", 0) > 50:
            severity = "Medium"

        # Store in DynamoDB
        table = dynamodb.Table('DisasterReport')
        report_id = str(uuid.uuid4())  # Generate a unique report ID

        table.put_item(Item={
            "ReportID": report_id,  # Ensure this matches the primary key name
            "type": report["type"],
            "location": report["location"],
            "severity": severity,
            "timestamp": report["timestamp"]
        })

        # If severity is High, send SNS alert
        if severity == "High":
            alert_message = f"🚨 Disaster Alert 🚨\nType: {report['type']}\nLocation: {report['location']}\nSeverity: {severity}\nTimestamp: {report['timestamp']}"
            send_alert(severity, alert_message)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Report processed", "severity": severity})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }