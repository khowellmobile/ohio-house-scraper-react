import classes from "./PeakModal.module.css";
import { useEffect, useState } from "react";

const PeakModal = ({ repInfo, handleCloseModal }) => {
    const [legislationList, setLegislationList] = useState();
    const [committeeList, setCommitteeList] = useState();

    useEffect(() => {
        if (repInfo["legislation"] !== "") {
            const legList = repInfo["legislation"].split("<newline>");
            setLegislationList(legList);
        }
    }, [repInfo]);

    useEffect(() => {
        if (repInfo["committees"] !== "") {
            const comList = repInfo["committees"].split(",");
            setCommitteeList(comList);
        }
    }, [repInfo]);

    const handleClose = () => {
        handleCloseModal();
    };

    const getInfo = (field) => {
        if (field.trim() === "" || field === null) {
            return "Information not ready";
        }
    
        return field;
    };
    
    return (
        <div className={classes.modalOverlay}>
            <div className={classes.mainContainer}>
                <button className={classes.closeButton} onClick={handleClose}>
                    Close
                </button>
                <div className={classes.infoListing}>
                    <p>Hometown:</p>
                    <div className={classes.singleItem}>{getInfo(repInfo["hometown"])}</div>
                    <p>Address:</p>
                    <div className={classes.singleItem}>{getInfo(repInfo["address"])}</div>
                    <p>Phone:</p>
                    <div className={classes.singleItem}>{getInfo(repInfo["phone"])}</div>
                    <p>Fax:</p>
                    <div className={classes.singleItem}>{getInfo(repInfo["fax"])}</div>
                    <p>Committees:</p>
                    <div className={classes.listItem}>{getInfo(repInfo["committees"])}</div>
                    <p>Legislation:</p>
                    <div className={classes.listItem}>
                        {legislationList && legislationList.length > 0
                            ? legislationList.map((val, index) => <div key={index}>{val}</div>)
                            : "Information not ready"}
                    </div>
                    <p>Education:</p>
                    <div className={classes.listItem}>{getInfo(repInfo["education"])}</div>
                    <p>Politics:</p>
                    <div className={classes.listItem}>{getInfo(repInfo["politics"])}</div>
                    <p>Employment:</p>
                    <div className={classes.listItem}>{getInfo(repInfo["employment"])}</div>
                    <p>Community:</p>
                    <div className={classes.listItem}>{getInfo(repInfo["community"])}</div>
                    <p>Image Formula:</p>
                    <div className={classes.singleItem}>{getInfo(repInfo["image_formula"])}</div>
                    <p>Image Url:</p>
                    <div className={classes.singleItem}>{getInfo(repInfo["image_url"])}</div>
                </div>
            </div>
        </div>
    );
};

export default PeakModal;
