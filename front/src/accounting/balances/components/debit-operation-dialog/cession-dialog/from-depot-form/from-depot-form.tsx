import { useFormContext } from "common/components/form2"
import { SessionDialogForm } from "../cession-dialog.types"
import { Autocomplete } from "common/components/autocomplete2"
import { Trans, useTranslation } from "react-i18next"
import * as common from "carbure/api"
import { normalizeDepot } from "carbure/utils/normalizers"
import { useState } from "react"
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
  const { value, bind } = useFormContext<SessionDialogForm>()
  const [volume, setVolume] = useState<number | undefined>()

  const handleChangeDepot = async (
    depot?: ReturnType<typeof normalizeDepot>["value"]
  ) => {
    if (depot) {
      const volume = await getVolumeByDepot(
        entity.id,
        balance.sector,
        balance.customs_category!,
        balance.biofuel!,
        depot.name
      )

      if (volume) {
        setVolume(volume)
      }
    }
  }
  return (
    <>
      <Autocomplete
        label={t("Sélectionnez un dépôt d'expédition")}
        getOptions={(search) => common.findDepots(search)}
        normalize={normalizeDepot}
        required
        {...bind("from_depot", {
          onChange: handleChangeDepot,
        })}
      />
      {value.from_depot && (
        <>
          {volume && volume > 0 && (
            <Notice noColor variant="info">
              <Trans>
                Solde disponible dans le dépôt {value.from_depot.name} :{" "}
                <strong>{formatNumber(volume, 0)} litres</strong>
              </Trans>
            </Notice>
          )}
          {volume === 0 && (
            <Notice noColor variant="warning">
              <Trans>
                Aucun solde disponible dans le dépôt {value.from_depot.name}
              </Trans>
            </Notice>
          )}
        </>
      )}
    </>
  )
}
