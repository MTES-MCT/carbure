import { useTranslation } from "react-i18next"

import useEntity from "common/hooks/entity"
import { UserRole } from "common/types"
import { useMutation } from "common/hooks/async"
import { Panel, LoaderOverlay, Row } from "common/components/scaffold"
import Checkbox from "common/components/checkbox"
import { Calculator } from "common/components/icons"
import Select from "common/components/select"
import * as api from "../api/company"

const CompanyOptions = () => {
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
  const toggleElec = useMutation(
    (toggle: boolean) => api.toggleElec(entity.id, toggle),
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

  const setPreferredUnit = useMutation(api.setEntityPreferredUnit, {
    invalidates: ["user-settings"],
  })

  const isLoading =
    toggleMAC.loading ||
    toggleStocks.loading ||
    toggleDirectDeliveries.loading ||
    toggleTrading.loading

  return (
    <Panel id="options">
      <header>
        <h1>{t("Options")}</h1>
      </header>

      <section>
        <p>
          {t(
            "Les options ci-dessous vous permettent de personnaliser l'interface de CarbuRe pour n'y montrer que les fonctionnalités pertinentes pour votre activité."
          )}
        </p>
      </section>

      <section>
        <Row style={{ alignItems: "center" }}>
          <Calculator size={18} style={{ marginRight: 16 }} />

          {t("Ma société préfère afficher les quantités en")}

          <Select
            variant="inline"
            value={entity.preferred_unit}
            onChange={(unit) => setPreferredUnit.execute(entity.id, unit!)}
            style={{ marginLeft: "var(--spacing-xs)" }}
            options={[
              {
                value: "l",
                label: t("litres (Éthanol à 20°, autres à 15°)"),
              },
              { value: "kg", label: t("kilogrammes") },
              { value: "MJ", label: t("mégajoules") },
            ]}
          />
        </Row>
      </section>

      <section>
        <Checkbox
          disabled={!canModify}
          label={t("Ma société gère un stock sur CarbuRe")}
          value={entity.has_stocks ?? false}
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
          value={entity.has_mac ?? false}
          onChange={toggleMAC.execute}
        />
        <Checkbox
          disabled={!canModify}
          label={t("Ma société effectue des livraisons directes")}
          value={entity.has_direct_deliveries}
          onChange={toggleDirectDeliveries.execute}
        />
        {entity.isOperator && (
          <Checkbox
            disabled={!canModify}
            label={t("Ma société accepte des volumes d'electricité")}
            value={entity.has_elec}
            onChange={toggleElec.execute}
          />
        )}
      </section>

      <footer />

      {isLoading && <LoaderOverlay />}
    </Panel>
  )
}

export default CompanyOptions
