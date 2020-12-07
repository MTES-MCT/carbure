import React from "react"
import { BrowserRouter } from "react-router-dom"

import { useApp } from "./hooks"

import { Redirect, Route, Switch } from "common/components/relative-route"

import { Alert } from "common/system/alert"
import { AlertTriangle } from "common/system/icons"
import NotificationsProvider from "common/system/notifications"

import Logout from "./routes/logout"
import Org from "./routes/org"

const CarbureApp = () => {
  const app = useApp()
  const { settings, getDefaultEntity } = app

  return (
    <BrowserRouter basename="/v2">
      <NotificationsProvider>
        <div id="app">
          {settings.error && (
            <Alert level="error" icon={AlertTriangle}>
              {settings.error}
            </Alert>
          )}

          {!settings.error && settings.data && (
            <Switch>
              <Route path="/org/:entity">
                <Org app={app} />
              </Route>

              <Route path="/logout">
                <Logout />
              </Route>

              <Redirect to={`/org/${getDefaultEntity()}`} />
            </Switch>
          )}
        </div>
      </NotificationsProvider>
    </BrowserRouter>
  )
}

export default CarbureApp
