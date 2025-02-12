import { useFormContext } from "common/components/form2"
import { SessionDialogForm } from "../cession-dialog.types"
import { Autocomplete } from "common/components/autocomplete2"
import { Trans, useTranslation } from "react-i18next"
import * as common from "carbure/api"
import { normalizeDepot } from "carbure/utils/normalizers"
import { useEffect, useState } from "react"
import { Notice } from "common/components/notice"
import { useQuery } from "common/hooks/async"
import { getVolumeByDepot } from "../api"
import useEntity from "carbure/hooks/entity"
import { Balance } from "accounting/balances/types"

type FromDepotProps = {
  balance: Balance
}

export const FromDepot = ({ balance }: FromDepotProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { value, bind } = useFormContext<SessionDialogForm>()
  const [volume, setVolume] = useState<number | undefined>()
  const { execute } = useQuery(getVolumeByDepot, {
    key: "volume-by-depot",
    params: [
      entity.id,
      balance.sector,
      balance.customs_category,
      balance.biofuel,
      value.from_depot,
    ],
    executeOnMount: false,
  })
  useEffect(() => {
    if (value.from_depot) {
      setVolume(1450)
    }
  }, [value.from_depot])

  return (
    <>
      <Autocomplete
        label={t("Sélectionnez un dépôt d'expédition")}
        getOptions={(search) => common.findDepots(search)}
        normalize={normalizeDepot}
        required
        {...bind("from_depot")}
      />
      {volume && (
        <Notice noColor>
          <Trans>Solde disponible dans le dépôt</Trans>
        </Notice>
      )}
    </>
  )
}
