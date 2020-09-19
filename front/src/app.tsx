import React from "react"
import { BrowserRouter, Route } from "react-router-dom"

import Topbar from "./components/top-bar"
import Transactions from "./routes/transactions"

const App = () => {
  return (
    <BrowserRouter basename="/v2">
      <Topbar />

      <Route path="/transactions">
        <Transactions />
      </Route>
    </BrowserRouter>
  )
}

export default App
