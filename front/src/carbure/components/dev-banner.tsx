import { useEffect, useRef, useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import Button from "common-v2/components/button"
import { AlertCircle } from "common-v2/components/icons"
import { Row } from "common-v2/components/scaffold"
import { isProduction } from "common-v2/utils/context"

const DevBanner = () => {
  const { t } = useTranslation()

  const [maximised, setMaximized] = useState(true)

  const HEIGHT = `var(--spacing-xl)`

  useEffect(() => {
    const header = document.querySelector("#app header") as HTMLElement
    if (header) header.style.marginTop = maximised ? HEIGHT : ""
  }, [maximised, HEIGHT])

  if (isProduction()) return null

  return (
    <Row
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        position: "fixed",
        top: 0,
        right: 0,
        width: maximised ? "100%" : HEIGHT,
        height: HEIGHT,
        backgroundColor: "#ffbb40dd",
        padding: maximised ? "var(--spacing-s) var(--main-spacing)" : 0,
        // opacity: maximised ? 1 : 0.75,
        zIndex: 10,
      }}
    >
      {maximised ? (
        <>
          <Trans>
            <b>Version de développement de CarbuRe :</b> les manipulations
            effectuées ici n'ont pas de répercussion et les déclarations ne sont
            pas prises en compte.
          </Trans>

          <Button
            asideX
            variant="link"
            label={t("Réduire")}
            action={() => setMaximized(false)}
          />
        </>
      ) : (
        <Button
          variant="icon"
          icon={<AlertCircle color="var(--orange-dark)" />}
          action={() => setMaximized(true)}
        />
      )}
    </Row>
  )
}

export default DevBanner
