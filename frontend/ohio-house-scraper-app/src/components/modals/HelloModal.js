import classes from "./HelloModal.module.css";

const HelloModal = ({ handleCloseModal }) => {
    const handleClose = () => {
        handleCloseModal();
    };

    return (
        <div className={classes.modalOverlay}>
            <div className={classes.mainContainer}>
                <h2>Welcome to The Ohio House Scraper</h2>
                <div className={classes.textContent}>
                    <h3>A few things to keep in mind:</h3>
                    <p>
                        The application is still a work in progress and may not function correctly in every case. Every
                        environment is unique, and new issues are being ironed out continuously.
                    </p>
                    <p>
                        If there are issues, set the toggle to "Saved". Saved mode uses saved information of a past run
                        of the scraper on 3/18/2025.
                    </p>
                    <p>
                        Improvements to the application are ongoing, so there may be some downtime when uploading a new
                        build.
                    </p>
                    <p>
                        The application's backend will run from 8:30 AM to 3:30 PM on weekdays. Outside these times, the
                        'Run Scraper' button will be locked.
                    </p>
                </div>
                <button className={classes.closeModalButton} onClick={handleClose}>
                    Lets Go!
                </button>
            </div>
        </div>
    );
};

export default HelloModal;
