import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import Button from "common/components/button"
import { AlertCircle } from "common/components/icons"
import { Row } from "common/components/scaffold"
import { isProduction } from "common/utils/production"
import cl from "clsx"
import styles from "./dev-banner.module.css"

export const DevBanner = () => {
  const { t } = useTranslation()
  const [maximized, setMaximized] = useState(true)

  if (isProduction()) return null

  return (
    <Row className={cl(styles["dev-banner"], !maximized && styles.minimized)}>
      {maximized ? (
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
