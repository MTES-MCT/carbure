import cl from "clsx"
import { Link } from "react-router-dom"
import { Trans, useTranslation } from "react-i18next"

import styles from "./footer.module.css"
import logoMTES from "../assets/images/MTE.svg"
import logoFabNum from "../assets/images/logo-fabriquenumerique.svg"
import logoBetaGouv from "../assets/images/betagouvfr.svg"
import logoFranceRelance from "../assets/images/france-relance.webp"
import logoEuropeanUnion from "../assets/images/union-europeenne.webp"
import { LinkedIn, Mail } from "common/components/icons"
import { Footer } from "common/components/scaffold"
import { MailTo } from "common/components/button"
import { useUser } from "carbure/hooks/user"

const CarbureFooter = () => {
  useTranslation()
  const user = useUser()

  return (
    <Footer className={styles.footer}>
      <div className={styles.footerUpper}>
        <ul className={styles.footerCarbureLinks}>
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
            <Link to="/stats" target="_blank" rel="noreferrer">
              <Trans>Statistiques publiques</Trans>
            </Link>
          </li>
          <li>
            <Link to="/double-counting-list" target="_blank" rel="noreferrer">
              <Trans>Double Comptage</Trans>
            </Link>
          </li>
        </ul>

        <ul className={styles.footerSocialLinks}>
          <li>
            <Trans>Nous contacter :</Trans>
          </li>
          {user.isAuthenticated() && (
            <li>
              <MailTo user="carbure" host="beta.gouv.fr">
                <Mail />
                <Trans>Email</Trans>
              </MailTo>
            </li>
          )}
          {/* <li>
            <a
              href="https://carbure-beta-gouv.slack.com/"
              target="_blank"
              rel="noreferrer"
            >
              <Slack />
              <Trans>Slack</Trans>
            </a>
          </li> */}
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
          <img
            src={logoMTES}
            alt="Logo MTES"
            className={cl(styles.footerMTES)}
          />
        </div>

        <div className={styles.footerTexts}>
          <p className={styles.footerDescription}>
            <Trans>
              CarbuRe est un service numérique de l'État incubé à la Fabrique
              numérique du Ministère de la Transition Écologique, membre du
              réseau d'incubateurs{" "}
              <a href="http://beta.gouv.fr">beta.gouv.fr</a>
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

      <div className={styles.footerPartners}>
        <div>
          <Trans>Nos partenaires :</Trans>
        </div>
        <div className={styles.footerPartnersLogos}>
          <img src={logoFabNum} alt="Logo Fabrique Numerique" />
          <img src={logoFranceRelance} alt="Logo France Relance" />
          <img src={logoEuropeanUnion} alt="Logo Union Européenne" />
          <img src={logoBetaGouv} alt="Logo Fabrique Numerique" />
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
            <Link to="/accessibilite">
              <Trans>Accessibilité : non conforme</Trans>
            </Link>
          </li>
        </ul>
      </div>
    </Footer>
  )
}

export default CarbureFooter
