import { PropsWithChildren } from "react"
import * as Sentry from "@sentry/react"

// Define sentry only if url is defined in .env AND environment is local
if (
  process.env.REACT_APP_SENTRY_DSN &&
  process.env.NODE_ENV !== "development"
) {
  Sentry.init({
    dsn: process.env.REACT_APP_SENTRY_DSN,
  })
}

const FallbackComponent = () => {
  return <div>An error has occured</div>
}

export const SentryProvider = ({ children }: PropsWithChildren) => {
  return (
    <Sentry.ErrorBoundary fallback={FallbackComponent} showDialog>
      {children}
    </Sentry.ErrorBoundary>
  )
}
