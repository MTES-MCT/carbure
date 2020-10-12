import React from "react"
import { BrowserRouter } from "react-router-dom"

import useApp from "./hooks/use-app"

import { LoaderOverlay } from "./components/system"
import { Redirect, Route, Switch } from "./components/relative-route"
import Exit from "./components/exit"

import Logout from "./routes/logout"
import Org from "./routes/org"

const App = () => {
  const { settings, getDefaultEntity } = useApp()

  if (settings.error) {
    return <Exit to="/" />
  }

  return (
    <BrowserRouter basename="/v2">
      {settings.loading && <LoaderOverlay />}

      {settings.data && (
        <Switch>
          <Route path="/org/:entity">
            <Org settings={settings} />
          </Route>

          <Route path="/logout">
            <Logout />
          </Route>

          {settings.data && <Redirect to={`/org/${getDefaultEntity()}`} />}
        </Switch>
      )}
    </BrowserRouter>
  )
}

export default App
