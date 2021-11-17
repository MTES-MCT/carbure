import { useTranslation } from "react-i18next"
import Autocomplete from "common-v2/components/autocomplete"
import { Fieldset, useBind } from "common-v2/components/form"
import { NumberInput, TextInput } from "common-v2/components/input"
import * as api from "common-v2/api"
import * as norm from "common-v2/utils/normalizers"
import { LotFormValue } from "./lot-form"

export const LotFields = () => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Lot")}>
      <TransportDocumentField />
      <VolumeField />
      <BiofuelField />
      <FeedstockField />
      <CountryOfOriginField />
      <FreeField />
    </Fieldset>
  )
}

export const TransportDocumentField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <TextInput
      required
      label={t("N° document d'accompagnement")}
      {...bind("transport_document_reference")}
    />
  )
}

export const VolumeField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <NumberInput
      required
      label={t("Volume en litres (Ethanol à 20°, autres à 15°)")}
      {...bind("volume")}
    />
  )
}

export const BiofuelField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const props = bind("biofuel")
  return (
    <Autocomplete
      required
      label={t("Biocarburant")}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={api.findBiofuels}
      normalize={norm.normalizeBiofuel}
      {...props}
    />
  )
}

export const FeedstockField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const props = bind("feedstock")
  return (
    <Autocomplete
      required
      label={t("Matière première")}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={api.findFeedstocks}
      normalize={norm.normalizeFeedstock}
      {...props}
    />
  )
}

export const CountryOfOriginField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  const props = bind("country_of_origin")
  return (
    <Autocomplete
      required
      label={t("Pays d'origine de la matière première")}
      defaultOptions={props.value ? [props.value] : undefined}
      getOptions={api.findCountries}
      normalize={norm.normalizeCountry}
      {...props}
    />
  )
}

export const FreeField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return <TextInput label={t("Champ libre")} {...bind("free_field")} />
}

export default LotFields
