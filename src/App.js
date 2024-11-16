import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
    const [userId, setUserId] = useState('');
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);
    const [socket, setSocket] = useState(null);
    const [receiverId, setReceiverId] = useState(''); // ID of the user we're chatting with

    useEffect(() => {
        // Only connect to WebSocket if userId is set
        if (userId) {
            const ws = new WebSocket('wss://aancyg26cf.execute-api.us-east-1.amazonaws.com/production/');
            ws.onopen = () => console.log('Connected to WebSocket');
            ws.onmessage = (event) => {
                const newMessage = JSON.parse(event.data);
                setMessages((prevMessages) => [...prevMessages, newMessage]);
            };
            ws.onclose = () => console.log('WebSocket closed');
            setSocket(ws);

            // Cleanup on unmount
            return () => ws.close();
        }
    }, [userId]);

    // Handle setting userId
    const handleSetUserId = () => {
        // Ask for userId only once
        if (!userId) {
            const inputUserId = prompt('Enter your User ID:');
            if (inputUserId) setUserId(inputUserId);
        }
    };

    // Function to send message
    const handleSendMessage = () => {
        if (socket && receiverId) {
            const messageData = {
                action: 'sendMessage',
                senderId: userId,
                receiverId: receiverId,
                content: message,
            };
            socket.send(JSON.stringify(messageData));
            setMessages([...messages, { senderId: userId, message: message }]);
            setMessage('');
        }
    };

    return ( <
        div className = "app-container" >
        <
        h1 > Real - Time Chat < /h1> <
        button onClick = { handleSetUserId } > Set User ID < /button> <
        input type = "text"
        placeholder = "Enter receiver ID"
        value = { receiverId }
        onChange = {
            (e) => setReceiverId(e.target.value)
        }
        /> <
        div className = "message-input-container" >
        <
        input type = "text"
        value = { message }
        onChange = {
            (e) => setMessage(e.target.value)
        }
        placeholder = "Type a message" /
        >
        <
        button onClick = { handleSendMessage } > Send < /button> < /
        div > <
        ul > {
            messages.map((msg, index) => ( <
                li key = { index } >
                <
                strong > { msg.senderId === userId ? 'You' : msg.senderId }: < /strong> {msg.message} < /
                li >
            ))
        } <
        /ul> < /
        div >
    );
}

export default App;