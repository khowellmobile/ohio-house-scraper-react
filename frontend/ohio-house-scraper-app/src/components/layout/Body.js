import classes from "./Body.module.css";
import { useState, useEffect, useRef } from "react";
import HelloModal from "../HelloModal";
import RepName from "../RepItem";

const Body = () => {
    const [messages, setMessages] = useState([]);
    const [isScraping, setIsScraping] = useState(false);
    const [csvJson, setCsvJson] = useState();
    const [isFullRun, setIsFullRun] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(true);

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
                        populateReps(message["msg"]);
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

    const populateReps = (names) => {
        names.forEach((name) => {
            setReps((prevReps) => ({
                ...prevReps,
                [name]: {},
            }));
        });
    };

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
    }, [reps]);

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

    const firstNames = [
        "John",
        "Jane",
        "Michael",
        "Sarah",
        "David",
        "Emily",
        "James",
        "Amanda",
        "Chris",
        "Jessica",
        "Daniel",
        "Olivia",
        "Ryan",
        "Samantha",
        "Matthew",
        "Sophia",
        "Andrew",
        "Isabella",
        "William",
        "Charlotte",
    ];
    const lastNames = [
        "Doe",
        "Smith",
        "Johnson",
        "Brown",
        "Taylor",
        "Anderson",
        "Davis",
        "Wilson",
        "Moore",
        "Jackson",
        "Martin",
        "Lee",
        "Perez",
        "Harris",
        "Clark",
        "Rodriguez",
        "Lewis",
        "Walker",
        "Young",
        "King",
    ];

    const generateRandomNames = () => {
        return Array.from({ length: 20 }, () => {
            const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
            const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
            return `${firstName} ${lastName}`;
        });
    };

    // State variable to store the random numbers
    const [repNames, setRepNames] = useState(generateRandomNames);

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
                    <button onClick={() => handleScraperCommand("get_rep_names")} disabled={isScraping}>
                        <p>Get Names</p>
                    </button>
                    <button onClick={() => convertJsonToCSV(csvJson)} disabled={isScraping}>
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
