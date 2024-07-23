import { Link, Navigate } from "react-router-dom"
import { Trans, useTranslation } from "react-i18next"
import { useUser } from "carbure/hooks/user"
import css from "./pending.module.css"
import { LoaderOverlay, Main } from "common/components/scaffold"
import Alert from "common/components/alert"
import { AlertTriangle, InfoCircle } from "common/components/icons"
import useTitle from "common/hooks/title"
import { MailTo } from "common/components/button"

const Pending = () => {
  const { t } = useTranslation()
  useTitle(t("Premiers pas"))

  const user = useUser()

  if (!user.isAuthenticated()) {
    return <Navigate replace to="/" />
  }

  if (user.hasEntities()) {
    const firstEntity = user.getFirstEntity()!
    return <Navigate replace to={`/org/${firstEntity.id}`} />
  }

  if (user.loading) {
    return <LoaderOverlay />
  }

  return (
    <Main className={css.container}>
      <header className={css.header}>
        <h1>
          <Trans>🌻 Bienvenue sur CarbuRe</Trans>
        </h1>
        <p>
          <Trans>La plateforme de gestion des flux de biocarburants</Trans>
        </p>
      </header>

      <section className={css.information}>
        <Alert variant="warning" className={css.pendingAlert}>
          <p>
            <AlertTriangle className={css.alertIcon} />{" "}
            <Trans>
              Il semblerait que votre compte ne soit lié à aucune entité
              enregistrée sur CarbuRe.
            </Trans>
          </p>

          <p>
            <Trans>
              Veuillez vous rendre sur la page{" "}
              <Link to="/account" className={css.link}>
                Mon Compte
              </Link>{" "}
              du menu pour effectuer une demande d'accès.
            </Trans>
          </p>
        </Alert>

        <Alert variant="info" className={css.pendingAlert}>
          <p>
            <InfoCircle className={css.faqIcon} />{" "}
            <Trans>
              Vous avez des questions concernant le fonctionnement de CarbuRe ?
            </Trans>
          </p>
          <p>
            <Trans>
              <a
                href="https://carbure-1.gitbook.io/faq/"
                target="_blank"
                rel="noreferrer"
                className={css.link}
              >
                Notre FAQ
              </a>{" "}
              contient de nombreuses ressources pouvant vous aider dans votre
              utilisation du produit.
            </Trans>
          </p>
        </Alert>

        <p className={css.info}>
          <Trans>
            Pour plus d'informations contactez nous sur{" "}
            <a
              href="https://carbure-beta-gouv.slack.com/"
              target="_blank"
              rel="noreferrer"
              className={css.link}
            >
              le Slack de CarbuRe
            </a>{" "}
            ou par e-mail à l'addresse{" "}
            <MailTo user="carbure" host="beta.gouv.fr" className={css.link}>
              disponible sur ce lien
            </MailTo>
            .
          </Trans>
        </p>
      </section>
    </Main>
  )
}

export default Pending
