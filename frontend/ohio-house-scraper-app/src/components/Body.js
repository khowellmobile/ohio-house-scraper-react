import classes from "./Body.module.css";

const Body = () => {
    return (
        <div className={classes.mainContainer}>
            <div className={classes.tools}>
                <button>
                    <p>Run Scraper</p>
                </button>
                <button>
                    <p>Save Output</p>
                </button>
            </div>
            <div className={classes.outputContainer}>
                <div className={classes.outputHeader}>
                    <h2>Status:</h2>
                </div>
                <div className={classes.output}></div>
            </div>
        </div>
    );
};

export default Body;
