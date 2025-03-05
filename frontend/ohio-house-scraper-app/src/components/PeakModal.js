import PeakItem from "./PeakItem.js";
import classes from "./PeakModal.module.css";
import { useEffect, useState } from "react";

const PeakModal = ({ repName, repInfo, handleCloseModal }) => {
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
            return "Unavailable";
        }

        return field;
    };

    return (
        <div className={classes.modalOverlay}>
            <div className={classes.mainContainer}>
                <div className={classes.header}>
                    <h2>{repName}</h2>
                    <button className={classes.closeButton} onClick={handleClose}>
                        Close
                    </button>
                </div>
                <div className={classes.infoListing}>
                    <PeakItem title="Hometown:" info={getInfo(repInfo["hometown"])} />
                    <PeakItem title="Address:" info={getInfo(repInfo["address"])} />
                    <PeakItem title="Phone:" info={getInfo(repInfo["phone"])} />
                    <PeakItem title="Fax:" info={getInfo(repInfo["fax"])} />
                    <PeakItem title="Committees:" info={getInfo(repInfo["committees"])} />
                    <PeakItem title="Legislation:" info="Unavailable" list={legislationList} />
                    <PeakItem title="Education:" info={getInfo(repInfo["education"])} />
                    <PeakItem title="Politics:" info={getInfo(repInfo["politics"])} />
                    <PeakItem title="Employment:" info={getInfo(repInfo["employment"])} />
                    <PeakItem title="Community:" info={getInfo(repInfo["community"])} />
                    <PeakItem title="Image Formula:" info={getInfo(repInfo["image_formula"])} />
                    <PeakItem title="Image Url:" info={getInfo(repInfo["image_url"])} />
                </div>
            </div>
        </div>
    );
};

export default PeakModal;
