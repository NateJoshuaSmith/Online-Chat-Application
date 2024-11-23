import pytest
from unittest.mock import MagicMock, patch
from ChatApp_Disconnect import lambda_handler  # Replace `app` with the filename where your Lambda function resides.

@pytest.fixture
def dynamodb_mock():
    """Mock the boto3 DynamoDB resource."""
    with patch('boto3.resource') as mock_resource:
        mock_dynamodb = MagicMock()
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_resource.return_value = mock_dynamodb
        yield mock_table

@pytest.fixture
def api_gateway_event():
    """Mock an API Gateway event with a connection ID."""
    return {
        "requestContext": {
            "connectionId": "test-connection-id"
        }
    }

def test_lambda_handler_success(dynamodb_mock, api_gateway_event):
    """Test successful execution of lambda_handler."""
    # Call the Lambda function
    response = lambda_handler(api_gateway_event, None)

    # Validate DynamoDB table.delete_item was called with the correct parameters
    dynamodb_mock.delete_item.assert_called_once_with(Key={'connectionId': 'test-connection-id'})

    # Validate the response
    assert response['statusCode'] == 200
    assert response['body'] == 'Disconnected successfully.'

def test_lambda_handler_missing_connection_id(dynamodb_mock):
    """Test execution when connection ID is missing."""
    event = {"requestContext": {}}  # Missing connectionId

    with pytest.raises(KeyError):
        lambda_handler(event, None)

def test_lambda_handler_delete_failure(dynamodb_mock, api_gateway_event):
    """Test execution when delete_item fails."""
    # Simulate a failure in delete_item
    dynamodb_mock.delete_item.side_effect = Exception("Delete failed")

    with pytest.raises(Exception, match="Delete failed"):
        lambda_handler(api_gateway_event, None)
