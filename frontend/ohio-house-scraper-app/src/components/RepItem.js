import classes from "./RepName.module.css";
import { ReactComponent as CheckedUserIcon } from "../assets/svgs/checked-user-icon.svg";
import { ReactComponent as QuestionUserIcon } from "../assets/svgs/question-user-icon.svg";
import { ReactComponent as PenUserIcon } from "../assets/svgs/pen-user-icon.svg";
import { ReactComponent as EyeIcon } from "../assets/svgs/eye-icon.svg";
import { ReactComponent as PlayIcon } from "../assets/svgs/play-icon.svg";
import { ReactComponent as ReRunIcon } from "../assets/svgs/refresh-icon.svg";

const RepName = ({ repName, status }) => {
    const getStatusIcon = () => {
        switch (status) {
            case "checked":
                return <CheckedUserIcon className={`${classes.statusIcon}`} />;
            case "pen":
                return <PenUserIcon className={`${classes.statusIcon} ${classes.hidden}`} />;
            case "question":
            default:
                return <QuestionUserIcon className={`${classes.statusIcon}`} />;
        }
    };

    return (
        <div className={classes.mainContainer}>
            <div className={classes.infoContainer}>
                <div className={classes.nameContainer}>
                    <p>{repName}</p>
                </div>
                <div className={classes.statusContainer}>{getStatusIcon()}</div>
            </div>
            <div className={classes.tools}>
                <EyeIcon className={classes.icon} />
                <PlayIcon className={classes.icon} />
                <ReRunIcon className={classes.icon} />
            </div>
        </div>
    );
};

export default RepName;
