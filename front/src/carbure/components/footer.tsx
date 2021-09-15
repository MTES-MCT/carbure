import cl from "clsx"
import { Trans } from "react-i18next"

import styles from "./footer.module.css"
import logoMTES from "../assets/images/MTE.svg"
import logoFabNum from "../assets/images/logo-fabriquenumerique.svg"
import logoBetaGouv from "../assets/images/betagouvfr.svg"
import { Link } from "common/components/relative-route"
import { ExternalLink, LinkedIn, Slack } from "common/components/icons"

const Footer = () => (
  <footer className={styles.footer}>
    <div className={styles.footerUpper}>
      <ul className={styles.footerCarbureLinks}>
        <li>
          <a
            href="https://carbure-1.gitbook.io/faq/"
            target="_blank"
            rel="noreferrer"
          >
            <Trans>Guide d'utilisation de CarbuRe</Trans>
            <ExternalLink />
          </a>
        </li>
        <li>
          <Link to="/public_stats" target="_blank" rel="noreferrer">
            <Trans>Statistiques publiques</Trans>
            <ExternalLink />
          </Link>
        </li>
      </ul>

      <ul className={styles.footerSocialLinks}>
        <li>
          <a
            href="https://carbure-beta-gouv.slack.com/"
            target="_blank"
            rel="noreferrer"
          >
            <Slack />
            <Trans>Slack</Trans>
          </a>
        </li>
        <li>
          <a
            href="https://www.linkedin.com/company/carbure-minist%C3%A8re-de-la-transition-%C3%A9cologique/"
            target="_blank"
            rel="noreferrer"
          >
            <LinkedIn />
            <Trans>LinkedIn</Trans>
          </a>
        </li>
      </ul>
    </div>

    <div className={styles.footerMiddle}>
      <div className={styles.footerLogos}>
        <img src={logoMTES} alt="Logo MTES" className={cl(styles.footerMTES)} />

        <img
          src={logoFabNum}
          alt="Logo Fabrique Numerique"
          className={styles.footerFanum}
        />

        <img
          src={logoBetaGouv}
          alt="Logo Fabrique Numerique"
          className={styles.footerBetagouv}
        />
      </div>

      <div className={styles.footerTexts}>
        <p className={styles.footerDescription}>
          <Trans>
            CarbuRe est un service numérique de l’État incubé à la Fabrique
            numérique du Ministère de la Transition Écologique, membre du réseau
            d’incubateurs <a href="http://beta.gouv.fr">beta.gouv.fr</a>
          </Trans>
        </p>

        <ul className={styles.footerGouvLinks}>
          <li>
            <a href="https://legifrance.gouv.fr">legifrance.gouv.fr</a>
          </li>
          <li>
            <a href="https://gouvernement.fr">gouvernement.fr</a>
          </li>
          <li>
            <a href="https://service-public.fr">service-public.fr</a>
          </li>
          <li>
            <a href="https://data.gouv.fr">data.gouv.fr</a>
          </li>
        </ul>
      </div>
    </div>

    <div className={styles.footerLower}>
      <ul className={styles.footerLegalLinks}>
        <li>
          <a
            target="_blank"
            href="https://carbure-1.gitbook.io/faq/mentions-legales-et-cgu/mentions-legales-et-conditions-generales-dutilisation"
            rel="noreferrer"
          >
            <Trans>Mentions légales</Trans>
          </a>
        </li>
        <li>
          <a
            target="_blank"
            href="https://carbure-1.gitbook.io/faq/mentions-legales-et-cgu/mentions-legales-et-conditions-generales-dutilisation#cookies"
            rel="noreferrer"
          >
            <Trans>Données personnelles et cookies</Trans>
          </a>
        </li>
        <li>
          <span className={styles.fakeLink}>
            <Trans>Accessibilité : non conforme</Trans>
          </span>
        </li>
      </ul>
    </div>
  </footer>
)

export default Footer
