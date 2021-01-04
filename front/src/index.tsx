import React from "react"
import ReactDOM from "react-dom"

import "./carbure/assets/css/index.css"
import * as serviceWorker from "./serviceWorker"
import Carbure from "./carbure"
import { BrowserRouter } from "react-router-dom"
import NotificationsProvider from "common/components/notifications"

ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter basename="/v2">
      <NotificationsProvider>
        <Carbure />
      </NotificationsProvider>
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById("root")
)

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister()
