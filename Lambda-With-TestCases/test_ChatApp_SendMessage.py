import pytest
from unittest.mock import MagicMock, patch
import json
import uuid
import time

from ChatApp_SendMessage import lambda_handler  # Adjust the import as per your file structure

# Mocked Event Fixture
@pytest.fixture
def api_gateway_event():
    """Mock API Gateway event."""
    return {
        'body': json.dumps({
            'senderId': 'user1',
            'receiverId': 'user2',
            'content': 'Hello, World!'
        })
    }

@pytest.fixture
def dynamodb_mock():
    """Mock the DynamoDB resource."""
    with patch('boto3.resource') as mock_resource:
        mock_dynamodb = MagicMock()
        mock_connections_table = MagicMock()
        mock_conversations_table = MagicMock()
        
        # Mock the Tables
        mock_dynamodb.Table.return_value = mock_connections_table
        mock_resource.return_value = mock_dynamodb
        yield mock_connections_table, mock_conversations_table

@pytest.fixture
def api_gateway_mock():
    """Mock the API Gateway management client."""
    with patch('boto3.client') as mock_client:
        mock_api_gateway = MagicMock()
        mock_client.return_value = mock_api_gateway
        yield mock_api_gateway

# Test Case 1: Test successful message sending
def test_lambda_handler_success(api_gateway_event, dynamodb_mock, api_gateway_mock):
    """Test the lambda_handler function for success scenario."""
    mock_connections_table, mock_conversations_table = dynamodb_mock
    mock_api_gateway = api_gateway_mock

    # Setup mock for DynamoDB and API Gateway methods
    mock_connections_table.scan.return_value = {'Items': [{'connectionId': 'connection1'}, {'connectionId': 'connection2'}]}
    
    # Call the Lambda function
    response = lambda_handler(api_gateway_event, None)

    # Validate that the message was stored in DynamoDB
    mock_conversations_table.put_item.assert_called_once_with(
        Item={
            'conversationId': 'user1_user2',
            'messageId': mock.ANY,  # Ensure the messageId is a uuid
            'senderId': 'user1',
            'receiverId': 'user2',
            'content': 'Hello, World!',
            'Timestamps': mock.ANY  # Ensure timestamp is added
        }
    )

    # Validate that the message was sent to all active connections
    mock_api_gateway.post_to_connection.assert_any_call(
        ConnectionId='connection1',
        Data=json.dumps({'senderId': 'user1', 'content': 'Hello, World!'})
    )
    mock_api_gateway.post_to_connection.assert_any_call(
        ConnectionId='connection2',
        Data=json.dumps({'senderId': 'user1', 'content': 'Hello, World!'})
    )

    # Validate the response
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['message'] == 'Message sent successfully'

# Test Case 2: Test failure when missing required fields in the event
def test_lambda_handler_missing_fields():
    """Test the lambda_handler when fields are missing in the event."""
    event = {
        'body': json.dumps({
            'senderId': 'user1',
            # Missing receiverId
            'content': 'Hello, World!'
        })
    }
    
    response = lambda_handler(event, None)
    assert response['statusCode'] == 500
    assert 'error' in json.loads(response['body'])

# Test Case 3: Test failure when DynamoDB put_item fails
def test_lambda_handler_dynamodb_failure(api_gateway_event, dynamodb_mock, api_gateway_mock):
    """Test the lambda_handler when DynamoDB put_item fails."""
    mock_connections_table, mock_conversations_table = dynamodb_mock
    mock_api_gateway = api_gateway_mock

    # Simulate a DynamoDB failure
    mock_conversations_table.put_item.side_effect = Exception("DynamoDB Error")

    response = lambda_handler(api_gateway_event, None)

    # Validate the response when there is an error
    assert response['statusCode'] == 500
    assert 'error' in json.loads(response['body'])

# Test Case 4: Test failure when API Gateway post_to_connection fails
def test_lambda_handler_api_gateway_failure(api_gateway_event, dynamodb_mock, api_gateway_mock):
    """Test the lambda_handler when API Gateway post_to_connection fails."""
    mock_connections_table, mock_conversations_table = dynamodb_mock
    mock_api_gateway = api_gateway_mock

    # Setup mock for DynamoDB and API Gateway methods
    mock_connections_table.scan.return_value = {'Items': [{'connectionId': 'connection1'}]}
    mock_api_gateway.post_to_connection.side_effect = Exception("API Gateway Error")

    response = lambda_handler(api_gateway_event, None)

    # Validate the response when there is an error
    assert response['statusCode'] == 500
    assert 'error' in json.loads(response['body'])

# Test Case 5: Test successful handling of multiple connections
def test_lambda_handler_multiple_connections(api_gateway_event, dynamodb_mock, api_gateway_mock):
    """Test lambda_handler when there are multiple active connections."""
    mock_connections_table, mock_conversations_table = dynamodb_mock
    mock_api_gateway = api_gateway_mock

    # Setup mock for DynamoDB to return multiple connections
    mock_connections_table.scan.return_value = {'Items': [{'connectionId': 'connection1'}, {'connectionId': 'connection2'}, {'connectionId': 'connection3'}]}
    
    # Call the Lambda function
    response = lambda_handler(api_gateway_event, None)

    # Ensure the message is sent to all 3 connections
    mock_api_gateway.post_to_connection.assert_any_call(ConnectionId='connection1', Data=json.dumps({'senderId': 'user1', 'content': 'Hello, World!'}))
    mock_api_gateway.post_to_connection.assert_any_call(ConnectionId='connection2', Data=json.dumps({'senderId': 'user1', 'content': 'Hello, World!'}))
    mock_api_gateway.post_to_connection.assert_any_call(ConnectionId='connection3', Data=json.dumps({'senderId': 'user1', 'content': 'Hello, World!'}))

    # Validate the response
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['message'] == 'Message sent successfully'
