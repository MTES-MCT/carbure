import { PropsWithChildren, useEffect } from "react"
import * as Sentry from "@sentry/react"
import Alert from "common/components/alert"
import { Trans, useTranslation } from "react-i18next"
import { MailTo } from "common/components/button"
import {
  useLocation,
  useNavigationType,
  createRoutesFromChildren,
  matchRoutes,
} from "react-router-dom"

export const initSentry = () => {
  // Define sentry only if url/env are defined in .env AND environment is not local
  if (
    import.meta.env.VITE_SENTRY_DSN &&
    import.meta.env.VITE_APP_ENV &&
    process.env.NODE_ENV !== "development"
  ) {
    Sentry.init({
      dsn: import.meta.env.VITE_SENTRY_DSN,
      environment: `carbure-${import.meta.env.VITE_APP_ENV}`,
      tracesSampleRate: 1.0,
      integrations: [
        Sentry.reactRouterV6BrowserTracingIntegration({
          useEffect,
          useLocation,
          useNavigationType,
          createRoutesFromChildren,
          matchRoutes,
        }),
        Sentry.replayIntegration(),
      ],
      // Session Replay
      replaysSessionSampleRate: 0.1, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
      replaysOnErrorSampleRate: 1.0, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
    })
  }
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
