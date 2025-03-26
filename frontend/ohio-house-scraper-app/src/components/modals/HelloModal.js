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
                    <h3>How to:</h3>
                    <p>
                        Select the fields you want scraped and click "Run Scraper". The represenative icons will change
                        to show progress.
                    </p>
                    <p>
                        Toggling to Saved mode will display data from a previous run of the scraper (3-18-2025). In the
                        event of any issues Saved mode will still work.
                    </p>
                    <p>
                        The application's backend will run from 8:30 AM to 3:30 PM on weekdays. Outside these times, use
                        Saved mode for information.
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
