import Body from "../components/sections/Body"
import Footer from "../components/sections/Footer"
import Header from "../components/sections/Header"
import classes from "./HomePage.module.css"

const HomePage = () => {
    return <div className={classes.mainContainer}>
        <Header />
        <Body />
        <Footer />
    </div>
}

export default HomePage