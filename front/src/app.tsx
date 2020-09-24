import React, { useState } from "react"
import { BrowserRouter, Route } from "react-router-dom"

import useAPI from "./hooks/use-api"
import { getSettings } from "./services/settings"

import Topbar from "./components/top-bar"
import Footer from "./components/footer"
import Logout from "./routes/logout"
import Transactions from "./routes/transactions"
import Exit from "./components/exit"

const App = () => {
  const [entity, setEntity] = useState(-1)

  const settings = useAPI(getSettings)
  settings.useResolve()

  // select the default entity if not already done
  if (entity === -1 && settings.data) {
    setEntity(settings.data.rights[0].entity.id)
  }

  if (settings.loading) {
    return <h1>Loading...</h1>
  }

  if (settings.error) {
    return <Exit to="/" />
  }

  return (
    <BrowserRouter basename="/v2">
      <Topbar settings={settings} entity={entity} setEntity={setEntity} />

      <Route path="/transactions">
        <Transactions settings={settings} entity={entity} />
      </Route>

      <Route path="/logout">
        <Logout />
      </Route>
      <Footer />
    </BrowserRouter>
  )
}

export default App
