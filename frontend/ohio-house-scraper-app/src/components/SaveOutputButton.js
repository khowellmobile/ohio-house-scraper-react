import classes from "./SaveOutputButton.module.css";

const SaveOutputButton = ({ reps, isScraping }) => {
    const downloadReps = () => {
        let headers;

        headers = [
            "Name",
            "Hometown",
            "Address",
            "Phone",
            "Fax",
            "Education",
            "Politics",
            "Employment",
            "Community",
            "Committees",
            "Legislation",
            "Image",
            "Image_URL",
        ];

        let csvContent = headers.join("\t") + "\n";

        Object.entries(reps).forEach(([key, name]) => {
            let row;
            row = [
                key,
                name.hometown,
                name.address,
                name.phone,
                name.fax,
                name.education,
                name.politics,
                name.employment,
                name.community,
                name.committees,
                name.legislation,
                name.image_formula,
                name.image_url,
            ].join("\t");

            csvContent += row + "\n";
        });

        const blob = new Blob([csvContent], { type: "text/plain" });

        // Create a download link for the CSV file
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "representatives_data.txt";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <button className={classes.mainContainer} onClick={() => downloadReps()} disabled={isScraping}>
            <p>Save Output</p>
        </button>
    );
};

export default SaveOutputButton;
