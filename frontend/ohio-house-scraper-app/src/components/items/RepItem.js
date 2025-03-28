import { useState } from "react";

import classes from "./RepItem.module.css";
import { ReactComponent as CheckedUserIcon } from "../../assets/svgs/checked-user-icon.svg";
import { ReactComponent as QuestionUserIcon } from "../../assets/svgs/question-user-icon.svg";
import { ReactComponent as PenUserIcon } from "../../assets/svgs/pen-user-icon.svg";
import { ReactComponent as EyeIcon } from "../../assets/svgs/eye-icon.svg";
import PeakModal from "../modals/PeakModal";

const RepItem = ({ repName, repInfo }) => {

    const [isModalOpen, setIsModalOpen] = useState(false);

    const handleCloseModal = () => {
        setIsModalOpen(false);
    };

    const handleOpenModal = () => {
        setIsModalOpen(true);
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case "checked":
                return <CheckedUserIcon className={`${classes.statusIcon}`} />;
            case "pen":
                return <PenUserIcon className={`${classes.statusIcon}`} />;
            case "question":
            default:
                return <QuestionUserIcon className={`${classes.statusIcon}`} />;
        }
    };

    return (
        <>
            {isModalOpen && <PeakModal repName={repName} repInfo={repInfo} handleCloseModal={handleCloseModal} />}

            <div className={classes.mainContainer}>
                <div className={classes.infoContainer}>
                    <div className={classes.nameContainer}>
                        <p>{repName}</p>
                    </div>
                    <div className={classes.statusContainer}>{getStatusIcon(repInfo["status"])}</div>
                </div>
                <div className={classes.tools}>
                    <EyeIcon className={classes.icon} onClick={handleOpenModal}/>
                </div>
            </div>
        </>
    );
};

export default RepItem;
