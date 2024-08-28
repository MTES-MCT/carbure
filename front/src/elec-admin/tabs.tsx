import { Loader } from "common/components/icons"
import Tabs from "common/components/tabs"
import { useTranslation } from "react-i18next"
import { ElecAdminSnapshot } from "./types"

interface ElecAdminTabsProps {
  loading: boolean
  snapshot: ElecAdminSnapshot
}

function ElecAdminTabs({ loading, snapshot }: ElecAdminTabsProps) {
  const { t } = useTranslation()

  return (
    <Tabs
      variant="main"
      tabs={[
        {
          key: "provision",
          path: "provision/available",
          label: (
            <>
              <p
                style={{
                  fontWeight: "normal",
                }}
              >
                {loading ? (
                  <Loader size={20} />
                ) : (
                  snapshot?.provision_certificates
                )}
                {/* {loading ? <Loader size={20} /> : formatNumber(snapshot?.provisioned_energy)} MWh */}
              </p>
              <strong>
                {/* {t("Énergie attribuée")} */}
                {t("Certificats de founiture")}
              </strong>
            </>
          ),
        },
        {
          key: "transfer",
          path: "transfer",
          label: (
            <>
              <p
                style={{
                  fontWeight: "normal",
                }}
              >
                {loading ? (
                  <Loader size={20} />
                ) : (
                  snapshot?.transfer_certificates
                )}
                {/* {loading ? <Loader size={20} /> : formatNumber(snapshot?.transferred_energy)} MWh */}
              </p>
              <strong>
                {t("Énergie cédée")}
                {/* {t("Énergie cédée")} */}
              </strong>
            </>
          ),
        },
      ]}
    />
  )
}

export default ElecAdminTabs
