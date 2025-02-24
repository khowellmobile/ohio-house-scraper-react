import Body from "../components/layout/Body"
import Footer from "../components/layout/Footer"
import Header from "../components/layout/Header"
import classes from "./HomePage.module.css"

const HomePage = () => {
    return <div className={classes.mainContainer}>
        <Header />
        <Body />
        <Footer />
    </div>
}

export default HomePage