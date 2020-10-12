import React from "react"

import { Settings } from "../services/types"
import { ApiState } from "../hooks/helpers/use-api"

import { Redirect, Route, Switch } from "../components/relative-route"
import Topbar from "../components/top-bar"
import Footer from "../components/footer"
import Transactions from "./transactions"

type MainProps = {
  settings: ApiState<Settings>
}

const Main = ({ settings }: MainProps) => (
  <React.Fragment>
    <Topbar settings={settings} />

    <Switch>
      <Route relative path="stocks">
        Stocks
      </Route>

      <Route relative path="transactions/:status">
        <Transactions />
      </Route>

      <Route relative path="controls">
        Contrôles
      </Route>

      <Route relative path="directory">
        Annuaire
      </Route>

      <Redirect relative to="transactions/draft" />
    </Switch>

    <Footer />
  </React.Fragment>
)

export default Main
