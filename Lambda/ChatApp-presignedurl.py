import boto3
import os
import uuid
import json

def lambda_handler(event, context):
    body = json.loads(event['body'])
    file_name = body['fileName']
    file_type = body['fileType']
    sender_id = body['senderId']
    receiver_id = body['receiverId']

    s3 = boto3.client('s3')
    bucket_name = "chatapp-file-storage"  # Update from your file

    file_key = f"{uuid.uuid4()}_{file_name}"
    presigned_url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': bucket_name,
            'Key': file_key,
            'ContentType': file_type,
        },
        ExpiresIn=3600
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'url': presigned_url, 'fileKey': file_key})
    }