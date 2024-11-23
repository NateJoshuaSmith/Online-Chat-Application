import boto3
import os

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    table_name = "ConnectionsTable"  # Update from your file details

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    table.delete_item(Key={'connectionId': connection_id})

    return {
        'statusCode': 200,
        'body': 'Disconnected successfully.'
    }