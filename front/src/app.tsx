import React from "react"
import { BrowserRouter, Route } from "react-router-dom"

import useApp from "./hooks/use-app"

import Exit from "./components/exit"
import Topbar from "./components/top-bar"
import Footer from "./components/footer"
import Logout from "./routes/logout"
import Transactions from "./routes/transactions"

const App = () => {
  const { entity, settings } = useApp()

  if (settings.loading) {
    return <h1>Loading...</h1>
  }

  if (settings.error) {
    return <Exit to="/" />
  }

  return (
    <BrowserRouter basename="/v2">
      <Topbar settings={settings} entity={entity} />

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
