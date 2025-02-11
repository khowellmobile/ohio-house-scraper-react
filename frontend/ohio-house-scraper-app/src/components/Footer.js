import classes from "./Footer.module.css";

const Footer = () => {
    return (
        <div className={classes.mainContainer}>
            <div className={classes.footerInfo}>
                <h3>Howell Associates</h3>
                <p>8720 Orion Place</p>
                <p>Columbus, OH 43240</p>
            </div>
            <div className={classes.links}>
                <a href="https://www.howellassociates.com/">HA Website</a>
                <a href="https://github.com/khowellmobile/ohio-house-scraper-react">GitHub</a>
                <a href="https://ohiohouse.gov/">OhioHouse.gov</a>
            </div>
        </div>
    );
};

export default Footer;
