import { useFormContext } from "common/components/form2"
import { SessionDialogForm } from "../cession-dialog.types"
import { Autocomplete } from "common/components/autocomplete2"
import { Trans, useTranslation } from "react-i18next"
import * as common from "carbure/api"
import { normalizeDepot } from "carbure/utils/normalizers"
import { Notice } from "common/components/notice"
import { getVolumeByDepot } from "../api"
import useEntity from "carbure/hooks/entity"
import { Balance } from "accounting/balances/types"
import { formatNumber } from "common/utils/formatters"

type FromDepotProps = {
  balance: Balance
}

export const FromDepotForm = ({ balance }: FromDepotProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind, setField } = useFormContext<SessionDialogForm>()

  const handleChangeDepot = async (
    depot?: ReturnType<typeof normalizeDepot>["value"]
  ) => {
    if (depot) {
      const volume = await getVolumeByDepot(
        entity.id,
        balance.sector,
        balance.customs_category,
        balance.biofuel!,
        depot.name
      )

      setField("from_depot_available_volume", volume ?? 0)
    }
  }
  return (
    <>
      <Autocomplete
        label={t("Sélectionnez un dépôt d'expédition")}
        placeholder={t("Rechercher un dépôt")}
        getOptions={(search) => common.findDepots(search)}
        normalize={normalizeDepot}
        required
        {...bind("from_depot", {
          onChange: handleChangeDepot,
        })}
      />
      {value.from_depot && (
        <>
          {value.from_depot_available_volume &&
          value.from_depot_available_volume > 0 ? (
            <Notice noColor variant="info">
              <Trans
                components={{ strong: <strong /> }}
                t={t}
                values={{
                  depot: value.from_depot.name,
                  volume: formatNumber(value.from_depot_available_volume, 0),
                }}
                defaults="Solde disponible dans le dépôt {{depot}} : <strong>{{volume}} litres</strong>"
              />
            </Notice>
          ) : null}
          {value.from_depot_available_volume === 0 ? (
            <Notice noColor variant="warning">
              <Trans
                t={t}
                values={{ depot: value.from_depot.name }}
                defaults="Aucun solde disponible dans le dépôt {{depot}}"
              />
            </Notice>
          ) : null}
        </>
      )}
    </>
  )
}
