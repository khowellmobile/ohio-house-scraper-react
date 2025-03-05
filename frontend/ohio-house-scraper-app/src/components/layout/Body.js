import classes from "./Body.module.css";
import { useState, useEffect } from "react";
import HelloModal from "../HelloModal";
import RepItem from "../RepItem";

const Body = () => {
    const [messages, setMessages] = useState([]);
    const [isScraping, setIsScraping] = useState(false);
    const [isFullRun, setIsFullRun] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(true);
    const [csvJson, setCsvJson] = useState();
    const [lockSocket, setLockSocket] = useState(false);
    const [reps, setReps] = useState({});

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
        if (lockSocket) {
            console.log("Web Socket currently in use. Wait a few minutes.");
            return;
        }

        setLockSocket(true);

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
                        handleRepUpdate(message);
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
            setLockSocket(false);
        };

        return () => {
            socket.close();
        };
    };

    const handleRepUpdate = (message) => {
        let status_mode;
        if ("rep_name" in message) {
            if (message["msg"].includes("Finished")) {
                status_mode = "checked";
            } else {
                status_mode = "pen";
            }

            setReps((prevReps) => {
                const updatedReps = { ...prevReps };

                if (updatedReps[message["rep_name"]]) {
                    updatedReps[message["rep_name"]] = {
                        ...updatedReps[message["rep_name"]],
                        status: status_mode,
                    };
                }

                return updatedReps;
            });
        }
    };

    const initializeReps = (names) => {
        const newReps = {};
        names.forEach((name) => {
            newReps[name] = {
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
                status: "question",
            };
        });
        setReps(newReps);
    };

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

    /** 
     * Populates reps with data when csvJson is recieved.
     * Will cause warning since React wants reps inside dependency array but that would cause
     * unwanted effects such as making reps match csv json anytime it is changed
    */
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

    // Will cause warning. Ignore the warning.
    useEffect(() => {
        handleScraperCommand("get_rep_names");
    }, []); // Empty to only run on mounts

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
                    <button onClick={() => downloadReps()} disabled={isScraping}>
                        <p>Save Output</p>
                    </button>
                    {isScraping && <div className={classes.spinner}></div>}
                </div>
                <div className={classes.repListing}>
                    {Object.entries(reps).map(([key, repInfo], index) => (
                        <RepItem key={index} repName={key} repInfo={repInfo} />
                    ))}
                </div>
            </div>
        </>
    );
};

export default Body;
