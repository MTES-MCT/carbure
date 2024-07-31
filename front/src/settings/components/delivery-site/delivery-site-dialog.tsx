import { Trans, useTranslation } from "react-i18next"
import {
  DepotType,
  EntityDepot,
  EntityType,
  OwnershipType,
} from "carbure/types"
import { TextInput } from "common/components/input"
import Button from "common/components/button"
import { Return } from "common/components/icons"
import { Dialog } from "common/components/dialog"
import { formatNumber, formatPercentage } from "common/utils/formatters"
import { DeliverySiteForm } from "./new-delivery-site-form"
import Form from "common/components/form"
import { RadioGroup } from "common/components/radio"
import { depotTypeOptions, ownerShipTypeOptions } from "./delivery-site.const"
import useEntity from "carbure/hooks/entity"
import Checkbox from "common/components/checkbox"
import { Row } from "common/components/scaffold"

type DeliverySiteDialogProps = {
  deliverySite: EntityDepot
  onClose: () => void
}

export const DeliverySiteDialog = ({
  deliverySite,
  onClose,
}: DeliverySiteDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const form = {
    name: deliverySite?.depot?.name ?? "",
    city: deliverySite?.depot?.city ?? "",
    country: deliverySite?.depot?.country ?? null,
    depot_id: deliverySite?.depot?.depot_id ?? "",
    depot_type: deliverySite?.depot?.depot_type ?? DepotType.Other,
    address: deliverySite?.depot?.address ?? "",
    postal_code: deliverySite?.depot?.postal_code ?? "",
    ownership_type: deliverySite?.ownership_type ?? OwnershipType.Own,
    blending_is_outsourced: deliverySite?.blending_is_outsourced ?? false,
    blender: deliverySite?.blender?.name ?? "",
    electrical_efficiency: deliverySite?.depot?.electrical_efficiency,
    thermal_efficiency: deliverySite?.depot?.thermal_efficiency,
    useful_temperature: deliverySite?.depot?.useful_temperature,
  }

  const depotType = deliverySite.depot?.depot_type ?? DepotType.Other
  const isPowerOrHeatPlant = [DepotType.PowerPlant, DepotType.HeatPlant, DepotType.CogenerationPlant].includes(depotType) // prettier-ignore

  const electricalEfficiency = deliverySite.depot?.electrical_efficiency
  const thermalEfficiency = deliverySite.depot?.thermal_efficiency
  const usefulTemperature = deliverySite.depot?.useful_temperature

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Détails du dépôt")}</h1>
      </header>

      <main>
        <section>
          <Form>
            <TextInput label={t("Nom du site")} value={form.name} readOnly />

            <TextInput
              label={t("Identifiant officiel")}
              value={form.depot_id}
              readOnly
            />

            <RadioGroup
              label={t("Type de dépôt")}
              value={form.depot_type}
              options={depotTypeOptions}
            />

            {entity.entity_type === EntityType.Operator && (
              <>
                <Checkbox
                  label={t("L'incorporation est effectuée par un tiers")}
                  value={form.blending_is_outsourced}
                  disabled
                />

                {form.blending_is_outsourced && (
                  <TextInput
                    label={t("Incorporateur Tiers")}
                    value={form.blender}
                    readOnly
                  />
                )}
              </>
            )}

            {form.electrical_efficiency && (
              <TextInput
                readOnly
                label={t("Rendement électrique")}
                value={formatPercentage(form.electrical_efficiency * 100)}
              />
            )}

            {form.electrical_efficiency && (
              <TextInput
                readOnly
                label={t("Rendement électrique")}
                value={formatPercentage(form.electrical_efficiency * 100)}
              />
            )}

            {form.electrical_efficiency && (
              <TextInput
                readOnly
                label={t("Rendement électrique")}
                value={formatPercentage(form.electrical_efficiency * 100)}
              />
            )}

            <TextInput readOnly label={t("Adresse")} value={form.address} />

            <Row style={{ gap: "var(--spacing-s)" }}>
              <TextInput readOnly label={t("Ville")} value={form.city} />
              <TextInput
                readOnly
                label={t("Code postal")}
                value={form.postal_code}
              />
            </Row>
            <TextInput
              readOnly
              label={t("Pays")}
              value={
                form.country
                  ? (t(form.country.code_pays, { ns: "countries" }) as string)
                  : ""
              }
            />
          </Form>
        </section>

        {isPowerOrHeatPlant && (
          <>
            <hr />
            <section>
              {electricalEfficiency && (
                <TextInput
                  readOnly
                  label={t("Rendement électrique")}
                  value={formatPercentage(electricalEfficiency * 100)}
                />
              )}
              {thermalEfficiency && (
                <TextInput
                  readOnly
                  label={t("Rendement thermique")}
                  value={formatPercentage(thermalEfficiency * 100)}
                />
              )}
              {usefulTemperature && (
                <TextInput
                  readOnly
                  label={t("Température utile")}
                  value={formatNumber(usefulTemperature) + "˚C"}
                />
              )}
            </section>
          </>
        )}

        <section></section>
      </main>

      <footer>
        <Button asideX icon={Return} action={onClose}>
          <Trans>Retour</Trans>
        </Button>
      </footer>
    </Dialog>
  )
}
