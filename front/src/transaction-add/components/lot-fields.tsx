import { useTranslation } from "react-i18next"
import Autocomplete from "common-v2/components/autocomplete"
import { Fieldset, useBind } from "common-v2/components/form"
import { NumberInput, TextInput } from "common-v2/components/input"
import * as api from "common-v2/api"
import * as norm from "common-v2/normalizers"
import { LotFormValue } from "./form"

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
  return (
    <Autocomplete
      required
      label={t("Biocarburant")}
      getOptions={api.findBiofuels}
      normalize={norm.normalizeBiofuel}
      {...bind("biofuel")}
    />
  )
}

export const FeedstockField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <Autocomplete
      required
      label={t("Matière première")}
      getOptions={api.findFeedstocks}
      normalize={norm.normalizeFeedstock}
      {...bind("feedstock")}
    />
  )
}

export const CountryOfOriginField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <Autocomplete
      required
      label={t("Pays d'origine de la matière première")}
      getOptions={api.findCountries}
      normalize={norm.normalizeCountry}
      {...bind("country_of_origin")}
    />
  )
}

export const FreeField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return <TextInput label={t("Champ libre")} {...bind("free_field")} />
}

export default LotFields
