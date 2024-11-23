import pytest
from unittest.mock import MagicMock, patch
import json
import uuid

from ChatApp_presignedurl import lambda_handler  # Adjust this import based on your file structure

# Mock Event Fixture
@pytest.fixture
def api_gateway_event():
    """Mock API Gateway event with file details."""
    return {
        'body': json.dumps({
            'fileName': 'testfile.jpg',
            'fileType': 'image/jpeg',
            'senderId': 'user1',
            'receiverId': 'user2'
        })
    }

# Test Case 1: Test successful generation of presigned URL
def test_lambda_handler_success(api_gateway_event):
    """Test the lambda_handler function for a successful presigned URL generation."""
    
    # Mock S3 client
    with patch('boto3.client') as mock_s3_client:
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = 'https://example.com/presigned-url'
        mock_s3_client.return_value = mock_s3
        
        # Call the Lambda function
        response = lambda_handler(api_gateway_event, None)

    # Validate that the presigned URL was generated with the correct parameters
    mock_s3.generate_presigned_url.assert_called_once_with(
        'put_object',
        Params={
            'Bucket': 'chatapp-file-storage',
            'Key': mock.ANY,  # The Key should be dynamically generated (UUID + file name)
            'ContentType': 'image/jpeg',
        },
        ExpiresIn=3600
    )

    # Validate the response
    response_body = json.loads(response['body'])
    assert response['statusCode'] == 200
    assert 'url' in response_body
    assert 'fileKey' in response_body

    # Ensure the fileKey follows the expected format: UUID + file name
    file_key = response_body['fileKey']
    assert file_key.startswith(str(uuid.UUID(file_key.split('_')[0])))  # Check if fileKey starts with a valid UUID

# Test Case 2: Test failure when body is missing required fields
def test_lambda_handler_missing_fields():
    """Test lambda_handler when required fields are missing in the event body."""
    event = {
        'body': json.dumps({
            # Missing 'fileName', 'fileType', 'senderId', or 'receiverId'
            'fileName': 'testfile.jpg'
        })
    }

    response = lambda_handler(event, None)
    assert response['statusCode'] == 500
    assert 'error' in json.loads(response['body'])

# Test Case 3: Test failure when S3 client raises an error
def test_lambda_handler_s3_error(api_gateway_event):
    """Test lambda_handler when S3 client raises an exception."""
    with patch('boto3.client') as mock_s3_client:
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.side_effect = Exception("S3 error")
        mock_s3_client.return_value = mock_s3

        response = lambda_handler(api_gateway_event, None)

    # Validate the response when there is an error
    assert response['statusCode'] == 500
    assert 'error' in json.loads(response['body'])

# Test Case 4: Test missing 'body' field in the event
def test_lambda_handler_missing_body():
    """Test lambda_handler when 'body' is missing in the event."""
    event = {}

    response = lambda_handler(event, None)
    assert response['statusCode'] == 500
    assert 'error' in json.loads(response['body'])
