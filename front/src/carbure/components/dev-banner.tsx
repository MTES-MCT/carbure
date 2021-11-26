import { Trans } from "react-i18next"

const DevBanner = () => {
  if (window.location.hostname === "carbure.beta.gouv.fr") return null

  return (
    <div
      style={{
        backgroundColor: "var(--orange-medium)",
        padding: "8px var(--main-spacing)",
      }}
    >
      <Trans>
        <b>Version de développement de CarbuRe :</b> les manipulations
        effectuées ici n'ont pas de répercussion et les déclarations ne sont pas
        prises en compte.
      </Trans>
    </div>
  )
}

export default DevBanner
