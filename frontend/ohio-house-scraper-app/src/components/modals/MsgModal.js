import classes from "./MsgModal.module.css"

const MsgModal = ({handleCloseModal, messages}) => {
    return (
        <div className={classes.modalOverlay}>
            <div className={classes.mainContainer}>
                <div className={classes.header}>
                <h2>Message Log:</h2>
                <button onClick={handleCloseModal}><p>Close</p></button>
                </div>
                <div className={classes.messages}>
                    {messages.map((value, index) => (
                        <p key={index}>{value}</p>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default MsgModal