import React from "react"

import { AppHook } from "../hooks/use-app"

import useEntity from "../hooks/helpers/use-entity"

import { Redirect, Route, Switch } from "../components/relative-route"
import Topbar from "../components/top-bar"
import Footer from "../components/footer"
import Transactions from "./transactions"
import Stocks from "./stock"
import Settings from "./settings"

type MainProps = {
  app: AppHook
}

const Org = ({ app }: MainProps) => {
  const entity = useEntity(app)

  if (!entity) {
    return <Redirect to="/" />
  }

  return (
    <React.Fragment>
      <Topbar entity={entity} settings={app.settings} />

      <Switch>
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
      </Switch>
      <Footer />
    </React.Fragment>
  )
}

export default Org
