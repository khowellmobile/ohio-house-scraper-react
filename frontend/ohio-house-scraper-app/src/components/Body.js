import classes from "./Body.module.css";
import { useState, useEffect, useRef } from "react";
import HelloModal from "./HelloModal";

const Body = () => {
    const [messages, setMessages] = useState([]);
    const [isScraping, setIsScraping] = useState(false);
    const [csvJson, setCsvJson] = useState();
    const [isFullRun, setIsFullRun] = useState(true);

    const [isModalOpen, setIsModalOpen] = useState(true);

    const scrollRef = useRef(null);

    const handleScraperCommand = (isFull) => {
        if (isFull) {
            handleScraper("start_full_scraper");
            setIsFullRun(true);
        } else {
            handleScraper("start_partial_scraper");
            setIsFullRun(false);
        }
    };

    const handleScraper = (initial_command) => {
        const socket = new WebSocket("ws://localhost:65432");

        socket.onopen = () => {
            console.log("Connected to WebSocket server");

            const message = {
                msg_type: "command",
                msg: initial_command,
            };

            socket.send(JSON.stringify(message));
            setIsScraping(true);
        };

        socket.onmessage = (event) => {
            let message;

            /* Checking is message json */
            try {
                message = JSON.parse(event.data);

                if ("msg_type" in message) {
                    if (message["msg_type"] === "update") {
                        setMessages((prevMessages) => [...prevMessages, message["msg"]]);
                    } else if (message["msg_type"] === "error") {
                        setMessages((prevMessages) => [...prevMessages, message["msg"]]);
                    }
                } else {
                    setCsvJson(message);
                }
            } catch (e) {
                message = "Not Json format. Printing plain message: " + event.data;
                setMessages((prevMessages) => [...prevMessages, message]);
            }
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            setMessages((prevMessages) => [...prevMessages, "WebSocket could not connect"]);
        };

        socket.onclose = () => {
            console.log("Disconnected from WebSocket server");
            setMessages((prevMessages) => [...prevMessages, "Closing WebSocket"]);
            setIsScraping(false);
        };

        return () => {
            socket.close();
        };
    };

    useEffect(() => {
        const container = scrollRef.current;
        container.scrollTop = container.scrollHeight;
    }, [messages]);

    useEffect(() => {
        if (csvJson) {
            console.log(csvJson);
        }
    }, [csvJson]);

    const convertJsonToCSV = (csvJson) => {
        let headers;

        if (isFullRun) {
            headers = [
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
        } else {
            headers = ["Name", "Legislation", "Image", "Image_URL"];
        }

        let csvContent = headers.join("\t") + "\n";

        for (const key in csvJson) {
            if (csvJson.hasOwnProperty(key)) {
                const person = csvJson[key];
                let row;

                if (isFullRun) {
                    row = [
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
                } else {
                    row = [key, person.legislation, person.image_formula, person.image_url].join("\t");
                }

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

    const handleCloseModal = () => {
        setIsModalOpen(false);
    };

    return (
        <>
            {isModalOpen && <HelloModal handleCloseModal={handleCloseModal} />}

            <div className={classes.mainContainer}>
                <div className={classes.tools}>
                    <button onClick={() => handleScraperCommand(true)} disabled={isScraping}>
                        <p>Run Full Scraper</p>
                    </button>
                    <button onClick={() => handleScraperCommand(false)} disabled={isScraping}>
                        <p>Run Legislative Scraper</p>
                    </button>
                    <button onClick={() => convertJsonToCSV(csvJson)} disabled={isScraping}>
                        <p>Save Output</p>
                    </button>
                </div>
                <div className={classes.outputContainer}>
                    <div className={classes.outputHeader}>
                        <h2>Status:</h2>
                    </div>
                    <div className={classes.output} ref={scrollRef}>
                        {messages.map((message, index) => (
                            <p key={index}>{message}</p>
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
};

export default Body;
