import { startReactDsfr } from "@codegouvfr/react-dsfr/spa"
import { Link } from "react-router-dom"
import i18n from "i18n"
declare module "@codegouvfr/react-dsfr/spa" {
  interface RegisterLink {
    Link: typeof Link
  }
}
startReactDsfr({
  defaultColorScheme: "light",
  Link: Link,
  useLang: function useLangDsfr() {
    return i18n.language
  },
})
