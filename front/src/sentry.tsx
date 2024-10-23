import { PropsWithChildren } from "react"
import * as Sentry from "@sentry/react"
import Alert from "common/components/alert"
import { Trans, useTranslation } from "react-i18next"
import { MailTo } from "common/components/button"

// Define sentry only if url/env are defined in .env AND environment is not local
if (
  import.meta.env.VITE_SENTRY_DSN &&
  import.meta.env.VITE_SENTRY_ENV &&
  process.env.NODE_ENV !== "development"
) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_SENTRY_ENV,
  })
}

const FallbackComponent = () => {
  const { t } = useTranslation()
  return (
    <Alert variant="danger" style={{ margin: "auto", textAlign: "center" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          flexDirection: "column",
          rowGap: "10px",
        }}
      >
        <p>
          {t("Nous sommes désolé, une erreur technique est survenue.")}
          <br />
          {t(
            "Merci de recharger la page ou nous contacter si le problème persiste."
          )}
        </p>
        <MailTo user="carbure" host="beta.gouv.fr">
          <Trans>Email</Trans>
        </MailTo>
      </div>
    </Alert>
  )
}

export const SentryProvider = ({ children }: PropsWithChildren) => {
  return (
    <Sentry.ErrorBoundary fallback={FallbackComponent} showDialog>
      {children}
    </Sentry.ErrorBoundary>
  )
}
