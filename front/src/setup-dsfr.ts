import { startReactDsfr } from "@codegouvfr/react-dsfr/spa"
import { Link } from "react-router-dom"
import "@codegouvfr/react-dsfr/dsfr/component/stepper/stepper.min.css"
import "@codegouvfr/react-dsfr/dsfr/component/input/input.min.css"
import "@codegouvfr/react-dsfr/dsfr/component/search/search.min.css"
import "@codegouvfr/react-dsfr/dsfr/component/button/button.min.css"
import "@codegouvfr/react-dsfr/dsfr/core/core.min.css"
import "@codegouvfr/react-dsfr/dsfr/utility/icons/icons.min.css"
import "@codegouvfr/react-dsfr/dsfr/component/notice/notice.min.css"
import "@codegouvfr/react-dsfr/dsfr/component/pagination/pagination.min.css"

declare module "@codegouvfr/react-dsfr/spa" {
  interface RegisterLink {
    Link: typeof Link
  }
}
startReactDsfr({ defaultColorScheme: "light", Link: Link })
