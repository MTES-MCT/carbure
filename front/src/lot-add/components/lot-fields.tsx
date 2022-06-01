import { useState } from "react"
import { useTranslation } from "react-i18next"
import Autocomplete, { AutocompleteProps } from "common/components/autocomplete"
import { Fieldset, useBind } from "common/components/form"
import {
  NumberInput,
  NumberInputProps,
  TextInput,
  TextInputProps,
} from "common/components/input"
import Select from "common/components/select"
import * as api from "common/api"
import * as norm from "common/utils/normalizers"
import { LotFormValue } from "./lot-form"
import { Biofuel, Country, Feedstock, Unit } from "common/types"
import useEntity from "carbure/hooks/entity"

interface LotFieldsProps {
  readOnly?: boolean
}

export const LotFields = (props: LotFieldsProps) => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Lot")}>
      <TransportDocumentField {...props} />
      <VolumeField {...props} />
      {/* <QuantityField {...props} /> */}
      <BiofuelField {...props} />
      <FeedstockField {...props} />
      <CountryOfOriginField {...props} />
      <FreeField {...props} />
    </Fieldset>
  )
}

export const TransportDocumentField = (props: TextInputProps) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <TextInput
      required
      label={t("N° document d'accompagnement")}
      {...bind("transport_document_reference")}
      {...props}
    />
  )
}

export const VolumeField = (props: NumberInputProps) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <NumberInput
      required
      label={t("Volume en litres (Ethanol à 20°, autres à 15°)")}
      {...bind("volume")}
      {...props}
    />
  )
}

export const QuantityField = (props: NumberInputProps) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const entity = useEntity()

  const [unit, setUnit] = useState<Unit | undefined>(entity.preferred_unit)

  const units = [
    { value: "l", label: t("litres") },
    { value: "kg", label: t("kg") },
    { value: "MJ", label: t("MJ") },
  ]

  const unitToField = {
    l: "volume" as "volume",
    kg: "weight" as "weight",
    MJ: "lhv_amount" as "lhv_amount",
  }

  return (
    <NumberInput
      required
      label={t("Quantité")}
      icon={
        <Select
          variant="text"
          value={unit}
          onChange={(u) => setUnit(u!)}
          options={units}
        />
      }
      {...bind(unitToField[unit ?? "l"])}
      {...props}
    />
  )
}

export const BiofuelField = (props: AutocompleteProps<Biofuel>) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const bound = bind("biofuel")
  return (
    <Autocomplete
      required
      label={t("Biocarburant")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findBiofuels}
      normalize={norm.normalizeBiofuel}
      {...bound}
      {...props}
    />
  )
}

export const FeedstockField = (props: AutocompleteProps<Feedstock>) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const bound = bind("feedstock")

  // prettier-ignore
  const icon = bound.value
    ? <span style={{ alignSelf: 'center', fontSize: '0.9em' }}>{bound.value.category.toUpperCase()}</span>
    : undefined

  return (
    <Autocomplete
      required
      icon={icon}
      label={t("Matière première")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findFeedstocks}
      normalize={norm.normalizeFeedstock}
      {...bound}
      {...props}
    />
  )
}

export const CountryOfOriginField = (props: AutocompleteProps<Country>) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const bound = bind("country_of_origin")
  return (
    <Autocomplete
      required
      label={t("Pays d'origine de la matière première")}
      defaultOptions={bound.value ? [bound.value] : undefined}
      getOptions={api.findCountries}
      normalize={norm.normalizeCountry}
      {...bound}
      {...props}
    />
  )
}

export const FreeField = (props: TextInputProps) => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <TextInput label={t("Champ libre")} {...bind("free_field")} {...props} />
  )
}

export default LotFields
