import classes from "./Body.module.css";
import { useState } from "react";

const Body = () => {
    const [messages, setMessages] = useState([]);
    const [isScraping, setIsScraping] = useState(false);
    const [csvJson, setCsvJson] = useState();

    function addMessage() {
        setMessages((prevMessages) => [...prevMessages, "HEllO"]);
        console.log("hello");
    }

    const handleScrapingStart = () => {
        const socket = new WebSocket("ws://localhost:65432");

        socket.onopen = () => {
            console.log("Connected to WebSocket server");
            socket.send("start_scraping");
            setIsScraping(true);
        };

        socket.onmessage = (event) => {
            console.log("Message from server:", event.data);

            let message;

            /* Checking is message is json */
            try {
                message = JSON.parse(event.data);
            } catch (e) {
                message = event.data;
                setMessages((prevMessages) => [...prevMessages, message]);
            }
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        socket.onclose = () => {
            console.log("Disconnected from WebSocket server");
            setIsScraping(false);
        };

        return () => {
            socket.close();
        };
    };

    const handleStopScraping = () => {
        setIsScraping(false);
    };

    return (
        <div className={classes.mainContainer}>
            <div className={classes.tools}>
                <button onClick={handleScrapingStart} disabled={isScraping}>
                    <p>Run Scraper</p>
                </button>
                <button onClick={handleStopScraping} disabled={!isScraping}>
                    <p>Save Output</p>
                </button>
                <button onClick={addMessage}>
                    <p>Add</p>
                </button>
            </div>
            <div className={classes.outputContainer}>
                <div className={classes.outputHeader}>
                    <h2>Status:</h2>
                </div>
                <div className={classes.output}>
                    {messages.map((message, index) => (
                        <p key={index}>{message}</p>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Body;
