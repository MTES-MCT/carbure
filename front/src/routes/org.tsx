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
  const entity = useEntity()

  if (!app.hasEntity(entity!)) {
    return <Redirect to="/" />
  }

  return (
    <React.Fragment>
      <Topbar settings={app.settings} entity={entity} />

      <Switch>
        <Route relative path="stocks">
          <Stocks />
        </Route>

        <Route relative path="transactions/:status">
          <Transactions />
        </Route>

        <Route relative path="settings">
          <Settings entity={entity} />
        </Route>

        <Redirect relative to="transactions/draft" />
      </Switch>
      <Footer />
    </React.Fragment>
  )
}

export default Org
