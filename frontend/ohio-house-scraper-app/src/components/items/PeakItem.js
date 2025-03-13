import classes from "./PeakItem.module.css";
import { ReactComponent as CopyIcon } from "../../assets/svgs/copy-icon.svg";
import { useEffect, useState } from "react";

const PeakItem = ({ title, info, list }) => {
    const [copyText, setCopyText] = useState();

    useEffect(() => {
        if (list && list.length > 0) {
            setCopyText(list.join("\n"));
        } else {
            setCopyText(info);
        }
    }, [list, info]);

    const handleCopyClick = () => {
        navigator.clipboard
            .writeText(copyText)
            .then(() => {
                alert("Text copied to clipboard!");
            })
            .catch((err) => {
                console.error("Failed to copy text: ", err);
            });
    };

    return (
        <>
            <p>{title}</p>
            <div className={classes.infoDiv}>
                <div className={classes.textContainer}>
                    {list && list.length > 0 ? list.map((val, index) => <div key={index}>{val}</div>) : <p>{info}</p>}
                </div>
                <CopyIcon className={classes.icon} onClick={handleCopyClick} />
            </div>
        </>
    );
};

export default PeakItem;
