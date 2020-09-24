import React from "react"

import styles from "./footer.module.css";
import logoMTES from "../assets/images/logo-mtes.svg"
import logoFabNum from "../assets/images/logo-fabriquenumerique.svg"

const Footer = () => (
  <div className={styles.footerContainer}>
    <div className={styles.flexCell}>
      <img src={logoMTES}
           alt="Logo MTES"
           className={styles.footerImage} />
    </div>

    <div className={styles.flexCell}>
      <img src={logoFabNum}
           alt="Logo Fabrique Numerique"
           className={styles.footerImage}
      />
    </div>

    <div className={styles.flexCell}>
      <p>
        CarbuRe est un service numérique de l’État incubé à la Fabrique
        numérique du Ministère de la Transition Écologique et Solidaire, membre
        du réseau d’incubateurs <a href="http://beta.gouv.fr"> beta.gouv.fr </a>
      </p>
    </div>

    <div className={styles.flexCell}>
      <ul>
        <li>
          <h2>carbure.beta.gouv.fr</h2>
        </li>
        <li>
          <a href="/">Conditions générales d'utilisation</a>
        </li>
        <li>
          <a href="https://metabase.carbure.beta.gouv.fr/public/dashboard/a9c045a5-c2fb-481a-ab85-f55bce8ae3c0">
            Statistiques
          </a>
        </li>
        <li>
          <a href="https://carbure-beta-gouv.slack.com/">
            Slack - Discussions, Support et Annonces
          </a>
        </li>
        <li>
          <a href="/">Glossaire</a>
        </li>
      </ul>
    </div>
  </div>
)

export default Footer