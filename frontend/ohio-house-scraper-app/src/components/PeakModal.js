import classes from "./PeakModal.module.css";

const PeakModal = ({ repInfo, handleCloseModal }) => {
    const handleClose = () => {
        handleCloseModal();
    };

    return (
        <div className={classes.modalOverlay}>
            <div className={classes.mainContainer}>
                <button className={classes.closeButton} onClick={handleCloseModal}>
                    Close
                </button>
                <p>Hometown: {repInfo["hometown"]}</p>
                <p>Address: {repInfo["address"]}</p>
                <p>Phone: {repInfo["phone"]}</p>
                <p>Fax: {repInfo["fax"]}</p>
                <p>Committees: {repInfo["committees"]}</p>
                <p>Legislation: {repInfo["legislation"]}</p>
                <p>Education: {repInfo["education"]}</p>
                <p>Politics: {repInfo["politics"]}</p>
                <p>Employment: {repInfo["employment"]}</p>
                <p>Community: {repInfo["community"]}</p>
                <p>Image Formula: {repInfo["image_formula"]}</p>
                <p>Image Url: {repInfo["image_url"]}</p>
            </div>
        </div>
    );
};

export default PeakModal;
