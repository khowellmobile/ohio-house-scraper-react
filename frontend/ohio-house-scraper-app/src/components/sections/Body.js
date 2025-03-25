import classes from "./Body.module.css";
import { useState, useEffect, useCallback } from "react";
import HelloModal from "../modals/HelloModal";
import RepItem from "../items/RepItem";
import MsgModal from "../modals/MsgModal";
import FieldDropdown from "../FieldDropdown";
import Toggle from "../Toggle";
import SaveOutputButton from "../SaveOutputButton";

import savedJsonData from "../../jsonData/savedScrape.json";
import savedRepNames from "../../jsonData/repNames.json";

const Body = () => {
    const [messages, setMessages] = useState([]);
    const [isScraping, setIsScraping] = useState(false);
    const [isHelloModalOpen, setIsHelloModalOpen] = useState(true);
    const [isMsgModalOpen, setIsMsgModalOpen] = useState(false);
    const [csvJson, setCsvJson] = useState();
    const [lockSocket, setLockSocket] = useState(false);
    const [reps, setReps] = useState({});
    const [useSaved, setUseSaved] = useState(false);

    const [fieldList, setFieldList] = useState([]);

    const handleScraperCommand = (command) => {
        if (useSaved && command !== "get_rep_names") {
            alert(
                "Please toggle to Current data mode in order to run the scraper. The page is currently set to Saved data mode"
            );
            return;
        }

        if (command === "start_scraper") {
            if (fieldList.length === 0) {
                alert("Please select at least one field set in the Selected Fields dropdown to run scraper");
                return;
            }
            handleScraper("start_scraper");
        } else if (command === "get_rep_names") {
            handleScraper("get_rep_names");
            setMessages((prevMessages) => [...prevMessages, "Getting Representative Names"]);
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

        /* const socket = new WebSocket("wss://wugtools.com:65432"); */
        const socket = new WebSocket("ws://localhost:50000");

        socket.onopen = () => {
            console.log("Connected to WebSocket server");

            const message = {
                msg_type: "command",
                msg: initial_command,
                fields: fieldList,
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

    const handleCloseHelloModal = () => {
        setIsHelloModalOpen(false);
    };

    const handleCloseMsgModal = () => {
        setIsMsgModalOpen(false);
    };

    const matchFieldLists = useCallback((list) => {
        setFieldList(list);
    }, []);

    const toggleSaved = useCallback((isSaved) => {
        setUseSaved(isSaved);
        if (isSaved) {
            initializeReps(savedRepNames["msg"]);

            // Spread operator required for change to trigger re-render
            setCsvJson({ ...savedJsonData });
        } else {
            handleScraperCommand("get_rep_names");
        }
    }, []);

    /*     useEffect(() => {
        console.log("useSaved: ", useSaved);
    }, [useSaved]); */

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
                        const updatedPerson = useSaved ? { ...person, status: "checked" } : { ...person };

                        setReps((prevReps) => ({
                            ...prevReps,
                            [name]: {
                                ...prevReps[name],
                                ...updatedPerson,
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
    }, []); // Empty to only run on mount

    return (
        <>
            {isHelloModalOpen && <HelloModal handleCloseModal={handleCloseHelloModal} />}
            {isMsgModalOpen && <MsgModal handleCloseModal={handleCloseMsgModal} messages={messages} />}

            <div className={classes.mainContainer}>
                <div className={classes.tools}>
                    <div className={classes.toolsLeft}>
                        <button onClick={() => handleScraperCommand("start_scraper")} disabled={isScraping && useSaved}>
                            <p>Run Scraper</p>
                            {isScraping && <div className={classes.spinner}></div>}
                        </button>
                        <FieldDropdown matchFieldLists={matchFieldLists} />
                    </div>
                    <div className={classes.toolsRight}>
                        <Toggle toggleSaved={toggleSaved} />
                        <button onClick={() => setIsMsgModalOpen(true)}>
                            <p>Message Log</p>
                        </button>
                    </div>
                </div>
                <div className={classes.repListing}>
                    {Object.entries(reps).map(([key, repInfo], index) => (
                        <RepItem key={index} repName={key} repInfo={repInfo} />
                    ))}
                    <SaveOutputButton reps={reps} isScraping={isScraping} />
                </div>
            </div>
        </>
    );
};

export default Body;
