import { startReactDsfr } from "@codegouvfr/react-dsfr/spa"
import { Link } from "react-router-dom"

declare module "@codegouvfr/react-dsfr/spa" {
  interface RegisterLink {
    Link: typeof Link
  }
}
startReactDsfr({ defaultColorScheme: "light", Link: Link })
