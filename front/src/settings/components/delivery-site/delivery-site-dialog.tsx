import { Trans, useTranslation } from "react-i18next"
import { DepotType, EntityDepot, OwnershipType } from "carbure/types"
import { TextInput } from "common/components/input"
import Button from "common/components/button"
import { Return } from "common/components/icons"
import { Dialog } from "common/components/dialog"
import { formatNumber, formatPercentage } from "common/utils/formatters"
import { DeliverySiteForm } from "./delivery-site-form"

type DeliverySiteDialogProps = {
  deliverySite: EntityDepot
  onClose: () => void
}

export const DeliverySiteDialog = ({
  deliverySite,
  onClose,
}: DeliverySiteDialogProps) => {
  const { t } = useTranslation()

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
          <DeliverySiteForm deliverySite={deliverySite} isReadOnly />
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
