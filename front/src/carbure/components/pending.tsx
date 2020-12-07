import styles from "./pending.module.css"

import { Link } from "common/components/relative-route"
import { Box, Main, Title } from "common/system"
import { Alert } from "common/system/alert"
import { AlertTriangle, Question } from "common/system/icons"

const Pending = () => (
  <Main className={styles.container}>
    <Title className={styles.welcome}>🌻 Bienvenue sur CarbuRe</Title>
    <p className={styles.subtitle}>
      La plateforme de gestion des flux de biocarburants
    </p>

    <Box className={styles.accountMessage}>
      <Alert level="warning" className={styles.pendingAlert}>
        <span>
          <AlertTriangle className={styles.alertIcon} />
          Il semblerait que votre compte ne soit lié à aucune entité enregistrée
          sur CarbuRe.
        </span>

        <span>
          Veuillez vous rendre vous sur la page
          <Link relative to="account" className={styles.link}>
            Mon Compte
          </Link>
          du menu pour effectuer une demande d'accès.
        </span>
      </Alert>

      <Alert level="info" className={styles.pendingAlert}>
        <span>
          <Question className={styles.faqIcon} />
          Vous avez des questions concernant le fonctionnement de CarbuRe ?
        </span>
        <span>
          <a href="/" target="_blank" rel="noreferrer" className={styles.link}>
            Notre FAQ
          </a>{" "}
          contient de nombreuses ressources pouvant vous aider dans votre
          utilisation du produit.
        </span>
      </Alert>

      <span className={styles.info}>
        Pour plus d'informations contactez nous sur
        <a
          href="https://carbure-beta-gouv.slack.com/"
          target="_blank"
          rel="noreferrer"
          className={styles.link}
        >
          le Slack de CarbuRe
        </a>
        ou par e-mail à l'addresse
        <a
          href="mailto:carbure@beta.gouv.fr"
          target="_blank"
          rel="noreferrer"
          className={styles.link}
        >
          carbure@beta.gouv.fr
        </a>
        .
      </span>
    </Box>
  </Main>
)

export default Pending
