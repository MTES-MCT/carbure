import React from "react"

import { AppHook } from "../hooks/use-app"

import useEntity from "../hooks/helpers/use-entity"

import { Redirect, Route, Switch } from "../components/relative-route"
import Topbar from "../components/top-bar"
import Footer from "../components/footer"
import Pending from "../components/pending"
import Exit from "../components/exit"
import Transactions from "./transactions"
import Stocks from "./stock"
import Settings from "./settings"
import Account from "./account"

type MainProps = {
  app: AppHook
}

const Org = ({ app }: MainProps) => {
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
          <Redirect relative to="draft" />
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

export default Org
