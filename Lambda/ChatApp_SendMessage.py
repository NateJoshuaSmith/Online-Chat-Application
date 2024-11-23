import boto3
import json
import os
import time
import uuid

def lambda_handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    connections_table = dynamodb.Table("ConnectionsTable")  
    conversations_table = dynamodb.Table("conversationsTable")  
    api_gateway = boto3.client('apigatewaymanagementapi', endpoint_url="https://aancyg26cf.execute-api.us-east-1.amazonaws.com/production")

    try:
        
        body = json.loads(event['body'])
        sender_id = body['senderId']
        receiver_id = body['receiverId']
        content = body['content']

        
        timestamp = int(time.time())
        message_id = str(uuid.uuid4())

        
        conversations_table.put_item(
            Item={
                'conversationId': f"{sender_id}_{receiver_id}",
                'messageId': message_id,
                'senderId': sender_id,
                'receiverId': receiver_id,
                'content': content,
                'Timestamps': timestamp  
            }
        )

        
        response = connections_table.scan()
        for item in response['Items']:
            connection_id = item['connectionId']
            try:
                
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
