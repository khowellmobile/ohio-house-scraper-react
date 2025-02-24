import classes from "./Body.module.css";
import { useState, useEffect, useRef } from "react";
import HelloModal from "../HelloModal";
import RepName from "../RepItem";

const Body = () => {
    const [messages, setMessages] = useState([]);
    const [isScraping, setIsScraping] = useState(false);
    const [isFullRun, setIsFullRun] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(true);
    const [csvJson, setCsvJson] = useState();

    const [lockNames, setLockedNames] = useState(false);

    const [reps, setReps] = useState({});
    const [chunks, setChunks] = useState([]);

    const handleScraperCommand = (command) => {
        if (command === "start_full_scraper") {
            handleScraper("start_full_scraper");
            setIsFullRun(true);
        } else if (command === "start_partial_scraper") {
            handleScraper("start_partial_scraper");
            setIsFullRun(false);
        } else if (command === "get_rep_names") {
            handleScraper("get_rep_names");
        } else {
            console.log("Not a recognized command");
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
                    } else if (message["msg_type"] === "data") {
                        initializeReps(message["msg"]);
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

    /* useEffect(() => {
        const container = scrollRef.current;
        container.scrollTop = container.scrollHeight;
    }, [messages]); */

    const initializeReps = (names) => {
        names.forEach((name) => {
            setReps((prevReps) => ({
                ...prevReps,
                [name]: {
                    hometown: "",
                    address: "",
                    phone: "",
                    fax: "",
                    education: "",
                    politics: "",
                    employment: "",
                    community: "",
                    committees: "",
                    legislation: "",
                    image_formula: "",
                    image_url: "",
                },
            }));
        });
    };

    useEffect(() => {
        if (csvJson) {
            const populateReps = () => {
                Object.entries(csvJson).forEach(([name, person]) => {
                    if (reps[name]) {
                        setReps((prevReps) => ({
                            ...prevReps,
                            [name]: {
                                ...prevReps[name],
                                ...person,
                            },
                        }));
                    }
                });
            };

            populateReps();
        }
    }, [csvJson]);

    const chunkArray = (array, size) => {
        const result = [];
        for (let i = 0; i < array.length; i += size) {
            result.push(array.slice(i, i + size));
        }
        return result;
    };

    useEffect(() => {
        const repNames = Object.keys(reps);
        const chunkedReps = chunkArray(repNames, 20);
        setChunks(chunkedReps);
        console.log(reps);
    }, [reps]);

    useEffect(() => {
        console.log(csvJson);
    }, [csvJson]);

    const downloadReps = () => {
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

        Object.entries(reps).forEach(([key, name]) => {
            let row;
            if (isFullRun) {
                row = [
                    key,
                    name.hometown,
                    name.address,
                    name.phone,
                    name.fax,
                    name.education,
                    name.politics,
                    name.employment,
                    name.community,
                    name.committees,
                ].join("\t");
            } else {
                row = [key, name.legislation, name.image_formula, name.image_url].join("\t");
            }

            csvContent += row + "\n";
        });

        const blob = new Blob([csvContent], { type: "text/plain" });

        // Create a download link for the CSV file
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "representatives_data.txt";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
    };

    return (
        <>
            {isModalOpen && <HelloModal handleCloseModal={handleCloseModal} />}

            <div className={classes.mainContainer}>
                <div className={classes.tools}>
                    <button onClick={() => handleScraperCommand("start_full_scraper")} disabled={isScraping}>
                        <p>Run Full Scraper</p>
                    </button>
                    <button onClick={() => handleScraperCommand("start_partial_scraper")} disabled={isScraping}>
                        <p>Run Legislative Scraper</p>
                    </button>
                    <button onClick={() => handleScraperCommand("get_rep_names")} disabled={lockNames}>
                        <p>Get Names</p>
                    </button>
                    <button onClick={() => downloadReps()} disabled={isScraping}>
                        <p>Save Output</p>
                    </button>
                </div>
                <div className={classes.repListing}>
                    {chunks.length > 0 && // Ensure chunks are available
                        chunks.map((chunk, index) => (
                            <div key={index}>
                                {chunk.map((name, subIndex) => (
                                    <RepName key={subIndex} repName={name} status={"question"} canRefresh={false} />
                                ))}
                            </div>
                        ))}
                </div>
            </div>
        </>
    );
};

export default Body;
