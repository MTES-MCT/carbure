import { startReactDsfr } from "@codegouvfr/react-dsfr/spa"
import { NavLink } from "react-router-dom"

declare module "@codegouvfr/react-dsfr/spa" {
  interface RegisterLink {
    Link: typeof NavLink
  }
}
startReactDsfr({ defaultColorScheme: "light", Link: NavLink })
