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
                        If the "Run Scraper" button is clicked and nothing happens, congratulations—you've found a bug
                        in the code! All bugs are promptly identified and stored to be fixed quickly.
                    </p>
                    <p>
                        Improvements to the application are ongoing, so there may be some downtime when uploading a new
                        build. In this case, come back in a few minutes, and it'll be up and running again.
                    </p>
                    <p>
                        To prevent surpassing AWS resource limits, the application's backend will run from 8:30 AM to
                        3:30 PM on weekdays. Outside these times, the 'Run Scraper' button will be locked.
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
