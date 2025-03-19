import classes from "./Toggle.module.css";
import { useEffect, useState } from "react";

const Toggle = ({ toggleSaved }) => {
    const [useSaved, setUseSaved] = useState(false);

    const toggle = () => {
        setUseSaved((prevState) => !prevState);
    };

    useEffect(() => {
        toggleSaved(useSaved);
    }, [useSaved, toggleSaved]);

    return (
        <div className={classes.mainContainer} onClick={toggle}>
            <div className={`${classes.thumb} ${useSaved ? classes.right : ""}`}></div>
            <div className={classes.words}>
                <div>
                    <p>Current</p>
                </div>
                <div>
                    <p>Saved</p>
                </div>
            </div>
        </div>
    );
};

export default Toggle;
