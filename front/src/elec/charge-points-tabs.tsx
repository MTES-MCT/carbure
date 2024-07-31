import Tabs from "common/components/tabs"
import { useTranslation } from "react-i18next"

export const ChargePointsTabs = () => {
  const { t } = useTranslation()

  return (
    <Tabs
      variant="main"
      tabs={[
        {
          key: "provisioned",
          path: "provisioned",
          label: (
            <>
              <p
                style={{
                  fontWeight: "normal",
                }}
              >
                MWh
              </p>
              <strong>{t("Énergie disponible")}</strong>
            </>
          ),
        },
        {
          key: "transferred",
          path: "transferred",
          label: (
            <>
              <p
                style={{
                  fontWeight: "normal",
                }}
              >
                MWh
              </p>
              <strong>{t("Énergie cédée")}</strong>
            </>
          ),
        },
      ]}
    />
  )
}
