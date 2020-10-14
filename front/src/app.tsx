import React from "react"
import { BrowserRouter } from "react-router-dom"

import useApp from "./hooks/use-app"

import { LoaderOverlay } from "./components/system"
import { Redirect, Route, Switch } from "./components/relative-route"
import Exit from "./components/exit"

import Logout from "./routes/logout"
import Org from "./routes/org"

const App = () => {
  const app = useApp()
  const { settings, getDefaultEntity } = app

  if (settings.error) {
    return <Exit to="/" />
  }

  return (
    <BrowserRouter basename="/v2">
      {settings.loading && <LoaderOverlay />}

      {settings.data && (
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
    </BrowserRouter>
  )
}

export default App
