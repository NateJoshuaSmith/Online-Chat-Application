import React, { useState, useEffect } from "react";

const ChatApp = () => {
        const [username, setUsername] = useState(""); // State for the username
        const [messages, setMessages] = useState([]);
        const [socket, setSocket] = useState(null);
        const [inputMessage, setInputMessage] = useState("");
        const [isConnected, setIsConnected] = useState(false);
        const [isUsernameSet, setIsUsernameSet] = useState(false); // State to check if username is set

        useEffect(() => {
            if (isUsernameSet) {
                // Initialize WebSocket
                const ws = new WebSocket(
                    "wss://aancyg26cf.execute-api.us-east-1.amazonaws.com/production"
                );
                setSocket(ws);

                // WebSocket open event
                ws.onopen = () => {
                    console.log("WebSocket connection established.");
                    setIsConnected(true);
                };

                // WebSocket message event
                ws.onmessage = (event) => {
                    const messageData = JSON.parse(event.data);

                    // Update messages state with the new message
                    setMessages((prevMessages) => [...prevMessages, messageData]);
                };

                // WebSocket error event
                ws.onerror = (error) => {
                    console.error("WebSocket error:", error);
                };

                // WebSocket close event
                ws.onclose = () => {
                    console.log("WebSocket connection closed.");
                    setIsConnected(false);
                };

                // Cleanup WebSocket on component unmount
                return () => {
                    ws.close();
                };
            }
        }, [isUsernameSet]);

        const handleSetUsername = () => {
            if (username.trim() !== "") {
                setIsUsernameSet(true);
            }
        };

        const sendMessage = () => {
            if (socket && socket.readyState === WebSocket.OPEN && inputMessage.trim() !== "") {
                const message = {
                    action: "sendMessage",
                    senderId: username, // Use the specified username
                    receiverId: "user2", // Update as needed
                    content: inputMessage,
                };

                socket.send(JSON.stringify(message));
                setInputMessage(""); // Clear the input box
            } else {
                console.error("WebSocket is not connected or message is empty.");
            }
        };

        if (!isUsernameSet) {
            return ( <
                div style = { styles.container } >
                <
                h1 > Chat App < /h1> <
                div style = { styles.usernameContainer } >
                <
                input type = "text"
                placeholder = "Enter your username..."
                value = { username }
                onChange = {
                    (e) => setUsername(e.target.value) }
                style = { styles.input }
                /> <
                button onClick = { handleSetUsername }
                style = { styles.button } >
                Set Username <
                /button> <
                /div> <
                /div>
            );
        }

        return ( <
            div style = { styles.container } >
            <
            h1 > Chat App < /h1> <
            div style = { styles.chatBox } > {
                messages.map((msg, index) => ( <
                    div key = { index }
                    style = { styles.message } >
                    <
                    strong > { msg.senderId }: < /strong> {msg.content} <
                    /div>
                ))
            } <
            /div> <
            div style = { styles.inputContainer } >
            <
            input type = "text"
            placeholder = "Type your message here..."
            value = { inputMessage }
            onChange = {
                (e) => setInputMessage(e.target.value) }
            style = { styles.input }
            /> <
            button onClick = { sendMessage }
            style = { styles.button } >
            Send <
            /button> <
            /div> {
                !isConnected && < p style = {
                        { color: "red" } } > Connecting to WebSocket... < /p>} <
                    /div>
            );
        };

        // Inline styles
        const styles = {
            container: {
                padding: "20px",
                fontFamily: "Arial, sans-serif",
            },
            chatBox: {
                border: "1px solid #ccc",
                borderRadius: "5px",
                padding: "10px",
                height: "300px",
                overflowY: "auto",
                marginBottom: "10px",
            },
            message: {
                marginBottom: "5px",
            },
            inputContainer: {
                display: "flex",
                gap: "10px",
            },
            input: {
                flex: 1,
                padding: "10px",
                borderRadius: "5px",
                border: "1px solid #ccc",
            },
            button: {
                padding: "10px 20px",
                backgroundColor: "#007bff",
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: "pointer",
            },
            usernameContainer: {
                display: "flex",
                gap: "10px",
                marginBottom: "20px",
            },
        };

        export default ChatApp;