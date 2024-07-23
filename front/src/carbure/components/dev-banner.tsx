import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import Button from "common/components/button"
import { AlertCircle } from "common/components/icons"
import { Row } from "common/components/scaffold"
import { isProduction } from "carbure/utils/production"

const DevBanner = () => {
  const { t } = useTranslation()
  const [maximised, setMaximized] = useState(true)

  if (isProduction()) return null

  return (
    <Row
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        position: maximised ? "sticky" : "fixed",
        top: 0,
        right: 0,
        width: maximised ? "100%" : "var(--spacing-xl)",
        height: "var(--spacing-xl)",
        backgroundColor: "#ffbb40dd",
        padding: maximised ? "var(--spacing-s) var(--main-spacing-x)" : 0,
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
