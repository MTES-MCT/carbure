import React from "react"
import { BrowserRouter } from "react-router-dom"

import useApp from "./hooks/use-app"

import { Redirect, Route, Switch } from "./components/relative-route"

import Logout from "./routes/logout"
import Org from "./routes/org"
import { Alert } from "./components/system/alert"
import { AlertTriangle } from "./components/system/icons"
import NotificationsProvider from "./components/system/notifications"

const App = () => {
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

export default App
