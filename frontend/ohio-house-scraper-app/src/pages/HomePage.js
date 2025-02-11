import Body from "../components/Body"
import Footer from "../components/Footer"
import Header from "../components/Header"
import classes from "./HomePage.module.css"

const HomePage = () => {
    return <div className={classes.mainContainer}>
        <Header />
        <Body />
        <Footer />
    </div>
}

export default HomePage