import Tooltip from "@codegouvfr/react-dsfr/Tooltip"
import { InfoCircle } from "common/components/icons"
import { Trans, useTranslation } from "react-i18next"

export const DoubleCountPeriod = ({
  startYear,
}: {
  startYear: number | undefined
}) => {
  const { t } = useTranslation()

  return (
    <div>
      <Tooltip
        title={t(
          `L'année détectée est renseignée en bas de l'onglet "Reconnaissance double comptage" du fichier excel.`
        )}
      >
        <Trans
          values={{
            period: startYear
              ? `${startYear} - ${startYear + 1}`
              : t("Non reconnue"),
          }}
          defaults="Période demandée : <b>{{ period }}</b>"
        />
        <InfoCircle
          color="#a4a4a4"
          size={15}
          style={{
            margin: "0px 0px 0 2px",
            position: "relative",
            top: "2px",
          }}
        />
      </Tooltip>
    </div>
  )
}
