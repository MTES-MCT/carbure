import { useTranslation } from "react-i18next"

import useEntity from "carbure/hooks/entity"
import { UserRole } from "carbure/types"
import { useMutation, useQuery } from "common-v2/hooks/async"
import { Panel, LoaderOverlay } from "common-v2/components/scaffold"
import Select from "common-v2/components/select"
import Checkbox from "common-v2/components/checkbox"
import * as api from "../api-v2"

const CompanySettings = () => {
  const { t } = useTranslation()
  const entity = useEntity()

  const canModify = entity.hasRights(UserRole.Admin, UserRole.ReadWrite)
  const { isTrader } = entity

  const certificates = useQuery(api.getMyCertificates, {
    key: "entity-certificates",
    params: [entity!.id],
  })

  const toggleMAC = useMutation(
    (toggle: boolean) => api.toggleMAC(entity.id, toggle),
    { invalidates: ["user-settings"] }
  )

  const toggleTrading = useMutation(
    (toggle: boolean) => api.toggleTrading(entity.id, toggle),
    { invalidates: ["user-settings"] }
  )

  const toggleStocks = useMutation(
    (toggle: boolean) => api.toggleStocks(entity.id, toggle),
    { invalidates: ["user-settings"] }
  )

  const toggleDirectDeliveries = useMutation(
    (toggle: boolean) => api.toggleDirectDeliveries(entity.id, toggle),
    { invalidates: ["user-settings"] }
  )

  const setDefaultCertificate = useMutation(
    (cert: string | undefined) => api.setDefaultCertificate(entity.id, cert!),
    { invalidates: ["user-settings"] }
  )

  const certificateData = certificates.result?.data.data ?? []

  const isLoading =
    certificates.loading ||
    toggleMAC.loading ||
    toggleStocks.loading ||
    toggleDirectDeliveries.loading ||
    toggleTrading.loading

  return (
    <Panel id="options" style={{ marginBottom: "var(--spacing-l)" }}>
      <header>
        <h1>{t("Options")}</h1>
      </header>

      <section>
        <Checkbox
          disabled={!canModify}
          label={t("Ma société effectue des mises à consommation")}
          value={entity.has_mac}
          onChange={toggleMAC.execute}
        />
        <Checkbox
          disabled={!canModify}
          label={t("Ma société effectue des livraisons directes")}
          value={entity.has_direct_deliveries || isTrader}
          onChange={toggleDirectDeliveries.execute}
        />

        <Checkbox
          disabled={!canModify}
          label={t("Ma société a une activité de négoce")}
          value={entity.has_trading || isTrader}
          onChange={toggleTrading.execute}
        />
        <Checkbox
          disabled={!canModify}
          label={t("Ma société gère un stock sur CarbuRe")}
          value={entity.has_stocks || isTrader}
          onChange={toggleStocks.execute}
        />
      </section>

      <footer>
        <Select
          label={t("Certificat par défaut")}
          placeholder={t("Sélectionner un certificat")}
          value={entity.default_certificate}
          onChange={setDefaultCertificate.execute}
          options={certificateData}
          style={{ flex: 1 }}
        />
      </footer>

      {isLoading && <LoaderOverlay />}
    </Panel>
  )
}

export default CompanySettings
