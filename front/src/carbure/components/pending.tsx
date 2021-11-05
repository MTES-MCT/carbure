import styles from "./pending.module.css"
import { Link, Navigate } from "react-router-dom"
import { Box, LoaderOverlay, Main, Title } from "common/components"
import { Alert } from "common/components/alert"
import { AlertTriangle, Question } from "common/components/icons"
import { Trans } from "react-i18next"
import { AppHook } from "carbure/hooks/use-app"

type PendingProps = {
  app: AppHook
}

const Pending = ({ app }: PendingProps) => {
  if (!app.isAuthenticated()) {
    return <Navigate to="/" />
  }

  if (app.hasEntities()) {
    const firstEntity = app.getFirstEntity()!
    return <Navigate to={`/org/${firstEntity.id}`} />
  }

  if (app.settings.loading || app.settings.data === null) {
    return <LoaderOverlay />
  }

  return (
    <Main className={styles.container}>
      <Title className={styles.welcome}>
        <Trans>🌻 Bienvenue sur CarbuRe</Trans>
      </Title>
      <p className={styles.subtitle}>
        <Trans>La plateforme de gestion des flux de biocarburants</Trans>
      </p>

      <Box className={styles.accountMessage}>
        <Alert level="warning" className={styles.pendingAlert}>
          <span>
            <AlertTriangle className={styles.alertIcon} />
            <Trans>
              Il semblerait que votre compte ne soit lié à aucune entité
              enregistrée sur CarbuRe.
            </Trans>
          </span>

          <span>
            <Trans>
              Veuillez vous rendre sur la page{" "}
              <Link to="/account" className={styles.link}>
                Mon Compte
              </Link>{" "}
              du menu pour effectuer une demande d'accès.
            </Trans>
          </span>
        </Alert>

        <Alert level="info" className={styles.pendingAlert}>
          <span>
            <Question className={styles.faqIcon} />
            <Trans>
              Vous avez des questions concernant le fonctionnement de CarbuRe ?
            </Trans>
          </span>
          <span>
            <Trans>
              <a
                href="https://carbure-1.gitbook.io/faq/"
                target="_blank"
                rel="noreferrer"
                className={styles.link}
              >
                Notre FAQ
              </a>{" "}
              contient de nombreuses ressources pouvant vous aider dans votre
              utilisation du produit.
            </Trans>
          </span>
        </Alert>

        <span className={styles.info}>
          <Trans>
            Pour plus d'informations contactez nous sur{" "}
            <a
              href="https://carbure-beta-gouv.slack.com/"
              target="_blank"
              rel="noreferrer"
              className={styles.link}
            >
              le Slack de CarbuRe
            </a>{" "}
            ou par e-mail à l'addresse{" "}
            <a
              href="mailto:carbure@beta.gouv.fr"
              target="_blank"
              rel="noreferrer"
              className={styles.link}
            >
              carbure@beta.gouv.fr
            </a>
            .
          </Trans>
        </span>
      </Box>
    </Main>
  )
}

export default Pending
