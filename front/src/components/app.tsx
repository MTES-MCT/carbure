import React from "react"
import { BrowserRouter } from "react-router-dom"

import Topbar from "./top-bar"

const App = () => {
  return (
    <BrowserRouter basename="/v2">
      <Topbar />
    </BrowserRouter>
  )
}

export default App
