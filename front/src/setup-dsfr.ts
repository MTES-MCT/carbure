import { startReactDsfr } from "@codegouvfr/react-dsfr/spa"
import { Link } from "react-router-dom"
import "@codegouvfr/react-dsfr/main.css"
declare module "@codegouvfr/react-dsfr/spa" {
  interface RegisterLink {
    Link: typeof Link
  }
}
startReactDsfr({ defaultColorScheme: "light", Link: Link })
