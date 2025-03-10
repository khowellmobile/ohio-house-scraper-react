import { useEffect, useState } from "react";
import classes from "./FieldDropdown.module.css";

const FieldDropdown = ({ matchFieldLists }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [fieldList, setFieldList] = useState([]);

    const toggleField = (fieldName) => {
        setFieldList((prevFieldList) => {
            // If the field is already in the list, remove it, else add it.
            if (prevFieldList.includes(fieldName)) {
                return prevFieldList.filter((field) => field !== fieldName);
            } else {
                return [...prevFieldList, fieldName];
            }
        });
    };

    const handleDropDownClick = (fieldName) => {
        toggleField(fieldName);
    };

    useEffect(() => {
        matchFieldLists(fieldList);
    }, [fieldList, matchFieldLists]);

    return (
        <div className={classes.mainContainer}>
            <div className={classes.title} onClick={() => setIsExpanded((prevIsExpanded) => !prevIsExpanded)}>
                <p>Selected Fields</p>
            </div>
            <div className={classes.dropDownArrow} onClick={() => setIsExpanded((prevIsExpanded) => !prevIsExpanded)}>
                <p>{isExpanded ? "△" : "▽"}</p>
            </div>
            {isExpanded && (
                <div className={classes.dropDown}>
                    <div className={classes.dropDownContent}>
                        <span
                            onClick={() => handleDropDownClick("info")}
                            className={fieldList.includes("info") ? classes.highlighted : ""}
                        >
                            General Information
                        </span>
                        <span
                            onClick={() => handleDropDownClick("bio")}
                            className={fieldList.includes("bio") ? classes.highlighted : ""}
                        >
                            Biography Information
                        </span>
                        <span
                            onClick={() => handleDropDownClick("committees")}
                            className={fieldList.includes("committees") ? classes.highlighted : ""}
                        >
                            Committees
                        </span>
                        <span
                            onClick={() => handleDropDownClick("legislation")}
                            className={fieldList.includes("legislation") ? classes.highlighted : ""}
                        >
                            Primary Legislation
                        </span>
                        <span
                            onClick={() => handleDropDownClick("image_url")}
                            className={fieldList.includes("image_url") ? classes.highlighted : ""}
                        >
                            Headshot
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FieldDropdown;
