import React from "react"
import { Link } from "react-router-dom"

import styles from "./logo.module.css"
import logoMarianne from "../assets/images/logo-marianne.svg"
import logoBetaGouv from "../assets/images/betagouvfr.svg"

const Logo = () => (
  <Link to="/" className={styles.logo}>
    <img src={logoMarianne} alt="marianne logo" className={styles.marianne} />
    <span className={styles.carbure}>carbure.</span>
    <img
      src={logoBetaGouv}
      alt="beta.gouv.fr logo"
      className={styles.betagouv}
    />
  </Link>
)

export default Logo
