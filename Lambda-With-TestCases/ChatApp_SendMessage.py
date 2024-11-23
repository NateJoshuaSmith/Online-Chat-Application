import boto3
import json
import os
import time
import uuid

def lambda_handler(event, context):
    # Initialize resources
    dynamodb = boto3.resource('dynamodb')
    connections_table = dynamodb.Table("ConnectionsTable")  # Update with your actual table name
    conversations_table = dynamodb.Table("conversationsTable")  # Update with your actual table name
    api_gateway = boto3.client('apigatewaymanagementapi', endpoint_url="https://aancyg26cf.execute-api.us-east-1.amazonaws.com/production")

    try:
        # Parse the incoming message
        body = json.loads(event['body'])
        sender_id = body['senderId']
        receiver_id = body['receiverId']
        content = body['content']

        # Generate timestamps and unique message ID
        timestamp = int(time.time())
        message_id = str(uuid.uuid4())

        # Save the message in the DynamoDB conversations table
        conversations_table.put_item(
            Item={
                'conversationId': f"{sender_id}_{receiver_id}",
                'messageId': message_id,
                'senderId': sender_id,
                'receiverId': receiver_id,
                'content': content,
                'Timestamps': timestamp  # Ensure this matches the DynamoDB schema
            }
        )

        # Fetch all active connections from the DynamoDB ConnectionsTable
        response = connections_table.scan()
        for item in response['Items']:
            connection_id = item['connectionId']
            try:
                # Send the message to all connected clients
                api_gateway.post_to_connection(
                    ConnectionId=connection_id,
                    Data=json.dumps({'senderId': sender_id, 'content': content})
                )
            except Exception as e:
                print(f"Failed to send message to connection {connection_id}: {e}")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Message sent successfully'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }