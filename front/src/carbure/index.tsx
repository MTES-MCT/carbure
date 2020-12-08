import React from "react"
import { BrowserRouter } from "react-router-dom"

import { AppHook, useApp } from "./hooks/use-app"
import useEntity from "./hooks/use-entity"

import { Alert } from "common/components/alert"
import { AlertTriangle } from "common/components/icons"
import NotificationsProvider from "common/components/notifications"

import { Redirect, Route, Switch } from "common/components/relative-route"
import Topbar from "./components/top-bar"
import Footer from "./components/footer"
import Pending from "./components/pending"
import Exit from "./components/exit"

import Transactions from "transactions"
import Stocks from "stocks"
import Settings from "settings"
import Account from "account"

// has to be nested in a route so we can get data from useParams()
const Org = ({ app }: { app: AppHook }) => {
  const { entity, pending } = useEntity(app)

  // a user with entities tries to access the pending or another entity's page
  if (app.hasEntities() && !entity) {
    return <Redirect to="/" />
  }

  // a user with no entities tries to access an entity page
  if (!app.hasEntities() && !pending) {
    return <Redirect to="/" />
  }

  return (
    <React.Fragment>
      <Topbar entity={entity} settings={app.settings} />

      <Switch>
        <Route relative exact path="account">
          <Account settings={app.settings} />
        </Route>

        <Route relative exact path="../pending">
          <Pending />
        </Route>

        <Route relative exact path="administration">
          <Exit to="/administrators/" />
        </Route>

        <Route relative exact path="stocks">
          <Redirect relative to="in" />
        </Route>

        <Route relative path="stocks/:status">
          <Stocks entity={entity} />
        </Route>

        <Route relative exact path="transactions">
          <Redirect relative to="draft" />
        </Route>

        <Route relative path="transactions/:status">
          <Transactions entity={entity} />
        </Route>

        <Route relative path="settings">
          <Settings entity={entity} settings={app.settings} />
        </Route>

        <Redirect relative to="transactions" />
      </Switch>

      <Footer />
    </React.Fragment>
  )
}

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
                <Exit to="/accounts/logout" />
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
