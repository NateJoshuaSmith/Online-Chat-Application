import pytest
from unittest.mock import MagicMock, patch
import json

from ChatApp_Connect import lambda_handler  # Adjust this import based on your file structure

# Test Case 1: Test successful connection handling
def test_lambda_handler_success():
    """Test lambda_handler function for successful connection setup."""
    
    # Mock the DynamoDB client
    with patch('boto3.resource') as mock_dynamodb_resource:
        mock_dynamodb = MagicMock()
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_dynamodb_resource.return_value = mock_dynamodb

        # Mock the event with a valid connection ID
        event = {
            'requestContext': {
                'connectionId': 'test-connection-id'
            }
        }
        
        # Call the lambda function
        response = lambda_handler(event, None)

        # Ensure the table's put_item method was called with the correct parameters
        mock_table.put_item.assert_called_once_with(Item={'connectionId': 'test-connection-id'})

        # Validate the response
        assert response['statusCode'] == 200
        assert response['body'] == 'Connected successfully.'

# Test Case 2: Test missing 'connectionId' in the event
def test_lambda_handler_missing_connection_id():
    """Test lambda_handler when 'connectionId' is missing in the event."""
    
    # Mock the DynamoDB client
    with patch('boto3.resource') as mock_dynamodb_resource:
        mock_dynamodb = MagicMock()
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_dynamodb_resource.return_value = mock_dynamodb

        # Mock the event without a connection ID
        event = {
            'requestContext': {}
        }

        with pytest.raises(KeyError):  # Expect a KeyError due to missing connectionId
            lambda_handler(event, None)

# Test Case 3: Test DynamoDB failure (e.g., put_item fails)
def test_lambda_handler_dynamodb_failure():
    """Test lambda_handler when DynamoDB put_item fails."""
    
    # Mock the DynamoDB client
    with patch('boto3.resource') as mock_dynamodb_resource:
        mock_dynamodb = MagicMock()
        mock_table = MagicMock()
        mock_table.put_item.side_effect = Exception("DynamoDB error")
        mock_dynamodb.Table.return_value = mock_table
        mock_dynamodb_resource.return_value = mock_dynamodb

        # Mock the event with a valid connection ID
        event = {
            'requestContext': {
                'connectionId': 'test-connection-id'
            }
        }

        # Call the lambda function
        response = lambda_handler(event, None)

        # Validate the response when there's an error
        assert response['statusCode'] == 500
        assert 'error' in json.loads(response['body'])

