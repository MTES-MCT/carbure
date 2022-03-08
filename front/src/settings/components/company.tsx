import { useTranslation } from "react-i18next"

import useEntity from "carbure/hooks/entity"
import { UserRole } from "carbure/types"
import { useMutation } from "common-v2/hooks/async"
import { Panel, LoaderOverlay } from "common-v2/components/scaffold"
import Checkbox from "common-v2/components/checkbox"
import * as api from "../api-v2"

const CompanySettings = () => {
  const { t } = useTranslation()
  const entity = useEntity()

  const canModify = entity.hasRights(UserRole.Admin, UserRole.ReadWrite)

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

  const isLoading =
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
        <p>
          {t(
            "Ces options vous permettent de personnaliser l'interface de la page Transactions de CarbuRe pour n'y montrer que les fonctionnalités pertinentes pour votre activité."
          )}
        </p>
      </section>

      <section style={{ paddingBottom: "var(--spacing-l)" }}>
        <Checkbox
          disabled={!canModify}
          label={t("Ma société gère un stock sur CarbuRe")}
          value={entity.has_stocks}
          onChange={toggleStocks.execute}
        />
        <Checkbox
          disabled={!canModify}
          label={t("Ma société a une activité de négoce")}
          value={entity.has_trading}
          onChange={toggleTrading.execute}
        />
        <Checkbox
          disabled={!canModify}
          label={t("Ma société effectue des mises à consommation (B100 et ED95 uniquement)")} // prettier-ignore
          value={entity.has_mac}
          onChange={toggleMAC.execute}
        />
        <Checkbox
          disabled={!canModify}
          label={t("Ma société effectue des livraisons directes")}
          value={entity.has_direct_deliveries}
          onChange={toggleDirectDeliveries.execute}
        />
      </section>

      {isLoading && <LoaderOverlay />}
    </Panel>
  )
}

export default CompanySettings
