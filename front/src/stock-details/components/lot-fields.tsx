import { useTranslation } from "react-i18next"
import Autocomplete, {
  AutocompleteProps,
} from "common-v2/components/autocomplete"
import { Fieldset, useBind, useFormContext } from "common-v2/components/form"
import {
  NumberInput,
  NumberInputProps,
  TextInput,
} from "common-v2/components/input"
import * as norm from "common-v2/utils/normalizers"
import { StockFormValue } from "./stock-form"
import { Biofuel, Country, Feedstock } from "common/types"
import { formatPercentage } from "common-v2/utils/formatters"
import { isRedII } from "lot-add/components/ghg-fields"

export const LotFields = () => {
  const { t } = useTranslation()
  const { value } = useFormContext<StockFormValue>()

  return (
    <Fieldset label={t("Stock")}>
      <VolumeField />
      <BiofuelField />
      <FeedstockField />
      <CountryOfOriginField />

      <TextInput
        asideY
        readOnly
        label={t("Réd. RED I")}
        value={formatPercentage(value.ghg_reduction ?? 0)}
      />
      {isRedII(value.delivery_date) && (
        <TextInput
          readOnly
          label={t("Réd. RED II")}
          value={formatPercentage(value.ghg_reduction_red_ii ?? 0)}
        />
      )}
    </Fieldset>
  )
}

export const VolumeField = (props: NumberInputProps) => {
  const { t } = useTranslation()
  const bind = useBind<StockFormValue>()
  return (
    <NumberInput
      readOnly
      label={t("Volume initial en litres (Ethanol à 20°, autres à 15°)")}
      {...bind("volume")}
      {...props}
    />
  )
}

export const BiofuelField = (props: AutocompleteProps<Biofuel>) => {
  const { t } = useTranslation()
  const bind = useBind<StockFormValue>()
  const bound = bind("biofuel")
  return (
    <Autocomplete
      readOnly
      label={t("Biocarburant")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      normalize={norm.normalizeBiofuel}
      {...bound}
      {...props}
    />
  )
}

export const FeedstockField = (props: AutocompleteProps<Feedstock>) => {
  const { t } = useTranslation()
  const bind = useBind<StockFormValue>()
  const bound = bind("feedstock")
  return (
    <Autocomplete
      readOnly
      label={t("Matière première")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      normalize={norm.normalizeFeedstock}
      {...bound}
      {...props}
    />
  )
}

export const CountryOfOriginField = (props: AutocompleteProps<Country>) => {
  const { t } = useTranslation()
  const bind = useBind<StockFormValue>()
  const bound = bind("country_of_origin")
  return (
    <Autocomplete
      readOnly
      label={t("Pays d'origine de la matière première")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      normalize={norm.normalizeCountry}
      {...bound}
      {...props}
    />
  )
}

export default LotFields
