import cl from "clsx"
import { Trans } from "react-i18next"

import styles from "./footer.module.css"
import logoMTES from "../assets/images/MTE.svg"
import logoFabNum from "../assets/images/logo-fabriquenumerique.svg"
import logoBetaGouv from "../assets/images/betagouvfr.svg"
import { Link } from "common/components/relative-route"
import { LinkedIn, Slack } from "common/components/icons"

const Footer = () => (
  <footer className={styles.footer}>
    <div className={styles.footerUpper}>
      <div>
        <img src={logoMTES} alt="Logo MTES" className={cl(styles.footerMTES)} />

        <img
          src={logoFabNum}
          alt="Logo Fabrique Numerique"
          className={styles.footerFanum}
        />
      </div>

      <div>
        <p className={styles.footerDescription}>
          <Trans>
            CarbuRe est un service numérique de l’État incubé à la Fabrique
            numérique du Ministère de la Transition Écologique, membre du réseau
            d’incubateurs <a href="http://beta.gouv.fr">beta.gouv.fr</a>
          </Trans>
        </p>
        <img
          src={logoBetaGouv}
          alt="Logo Fabrique Numerique"
          className={styles.footerBetagouv}
        />
      </div>
    </div>

    <div className={styles.footerLinks}>
      <ul className={styles.footerCarbureLinks}>
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
          <Link to="/public_stats">
            <Trans>Statistiques</Trans>
          </Link>
        </li>
      </ul>

      <ul className={styles.footerSocialLinks}>
        <li>
          <Slack />
          <a href="https://carbure-beta-gouv.slack.com/">
            <Trans>Slack</Trans>
          </a>
        </li>
        <li>
          <LinkedIn />
          <a href="https://www.linkedin.com/company/carbure-minist%C3%A8re-de-la-transition-%C3%A9cologique/">
            <Trans>LinkedIn</Trans>
          </a>
        </li>
      </ul>
    </div>
  </footer>
)

export default Footer
