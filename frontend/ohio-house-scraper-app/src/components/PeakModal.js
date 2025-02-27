import classes from "./PeakModal.module.css";

const PeakModal = ({ handleCloseModal }) => {
    const handleClose = () => {
        handleCloseModal();
    };

    return (
        <div className={classes.modalOverlay}>
            <div className={classes.mainContainer}>
                <button className={classes.closeButton} onClick={handleCloseModal}>
                    Close
                </button>
            </div>
        </div>
    );
};

export default PeakModal;
