import cl from "clsx"
import { Trans } from "react-i18next"

import styles from "./footer.module.css"
import logoMTES from "../assets/images/MTE.svg"
import logoFabNum from "../assets/images/logo-fabriquenumerique.svg"

const Footer = () => (
  <footer className={styles.footerContainer}>
    <div className={styles.flexCell}>
      <div className={styles.centerImage}>
        <img
          src={logoMTES}
          alt="Logo MTES"
          className={cl(styles.footerImage, styles.footerMTES)}
        />
      </div>
    </div>

    <div className={styles.flexCell}>
      <div className={styles.centerImage}>
        <img
          src={logoFabNum}
          alt="Logo Fabrique Numerique"
          className={styles.footerImage}
        />
      </div>
    </div>

    <div className={styles.flexCell}>
      <p>
        <Trans>
          CarbuRe est un service numérique de l’État incubé à la Fabrique
          numérique du Ministère de la Transition Écologique, membre du réseau
          d’incubateurs <a href="http://beta.gouv.fr">beta.gouv.fr</a>
        </Trans>
      </p>
    </div>

    <div className={styles.flexCell}>
      <ul className={styles.footerLinks}>
        <li>
          <h2>carbure.beta.gouv.fr</h2>
        </li>
        <li>
          <a
            target="_blank"
            href="https://carbure-1.gitbook.io/faq/mentions-legales-et-cgu/mentions-legales-et-conditions-generales-dutilisation#cookies"
            rel="noreferrer"
          >
            <Trans>Cookies</Trans>
          </a>
        </li>
        <li>
          <a
            target="_blank"
            href="https://carbure-1.gitbook.io/faq/mentions-legales-et-cgu/mentions-legales-et-conditions-generales-dutilisation"
            rel="noreferrer"
          >
            <Trans>Conditions générales d'utilisation</Trans>
          </a>
        </li>
        <li>
          <a
            href="https://carbure-1.gitbook.io/faq/"
            target="_blank"
            rel="noreferrer"
          >
            <Trans>Guide d'utilisation de CarbuRe</Trans>
          </a>
        </li>
        <li>
          <a href="https://metabase.carbure.beta.gouv.fr/public/dashboard/a9c045a5-c2fb-481a-ab85-f55bce8ae3c0">
            <Trans>Statistiques</Trans>
          </a>
        </li>
        <li>
          <a href="https://carbure-beta-gouv.slack.com/">
            <Trans>Slack - Discussions, Support et Annonces</Trans>
          </a>
        </li>

        <li>
          <a href="/">
            <Trans>Glossaire</Trans>
          </a>
        </li>
      </ul>
    </div>
  </footer>
)

export default Footer
