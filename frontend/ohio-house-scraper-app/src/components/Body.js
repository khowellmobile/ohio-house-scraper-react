import classes from "./Body.module.css";
import { useState, useEffect } from "react";

const Body = () => {
    const [messages, setMessages] = useState([]);
    const [isScraping, setIsScraping] = useState(false);
    const [csvJson, setCsvJson] = useState();

    const handleScrapingStart = () => {
        const socket = new WebSocket("ws://localhost:65432");

        socket.onopen = () => {
            console.log("Connected to WebSocket server");
            socket.send("start_scraping");
            setIsScraping(true);
        };

        socket.onmessage = (event) => {
            let message;

            /* Checking is message json */
            try {
                message = JSON.parse(event.data);
                setCsvJson(message);
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

    useEffect(() => {
        if (csvJson) {
            console.log(csvJson);
        }
    }, [csvJson]);

    const convertJsonToCSV = (csvJson) => {
        const headers = [
            "Name",
            "Hometown",
            "Address",
            "Phone",
            "Fax",
            "Education",
            "Politics",
            "Employment",
            "Community",
            "Committees",
        ];

        let csvContent = headers.join("\t") + "\n"; 

        for (const key in csvJson) {
            if (csvJson.hasOwnProperty(key)) {
                const person = csvJson[key];
                const row = [
                    key,
                    person.hometown,
                    person.address,
                    person.phone,
                    person.fax,
                    person.education,
                    person.politics,
                    person.employment,
                    person.community,
                    person.committees,
                ].join("\t");

                csvContent += row + "\n";
            }
        }

        const blob = new Blob([csvContent], { type: "text/plain" });

        // Create a download link for the CSV file
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "representatives_data.txt";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        console.log(csvJson);
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
                <button onClick={() => convertJsonToCSV(csvJson)} disabled={isScraping}>
                    <p>Save Output</p>
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
