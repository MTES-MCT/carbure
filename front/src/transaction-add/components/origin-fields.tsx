import { useTranslation } from "react-i18next"
import Autocomplete from "common-v2/components/autocomplete"
import { Fieldset, useBind, useFormContext } from "common-v2/components/form"
import { TextArea } from "common-v2/components/input"
import * as api from "common-v2/api"
import * as norm from "common-v2/normalizers"
import { LotFormValue } from "./form"
import { UserCheck } from "common-v2/components/icons"

export const OriginFields = () => {
  const { t } = useTranslation()
  return (
    <Fieldset label={t("Provenance")}>
      <ProducerField />
      <SupplierField />
      <SupplierCertificateField />
      <FreeField />
    </Fieldset>
  )
}

export const ProducerField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return (
    <Autocomplete
      label={t("Producteur")}
      getOptions={api.findEntities}
      create={norm.identity}
      normalize={norm.normalizeEntity}
      {...bind("producer")}
    />
  )
}

export const SupplierField = () => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const isKnown = value.lot && value.lot.carbure_supplier !== null
  return (
    <Autocomplete
      label={t("Fournisseur")}
      getOptions={api.findEntities}
      normalize={norm.normalizeEntity}
      icon={isKnown ? UserCheck : undefined}
      {...bind("supplier")}
    />
  )
}

export const SupplierCertificateField = () => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<LotFormValue>()
  const entity_id = norm.id(value.supplier)
  return (
    <Autocomplete
      label={t("Certificat du fournisseur")}
      getOptions={(query) => api.findCertificates(query, { entity_id })}
      {...bind("supplier_certificate")}
    />
  )
}

export const FreeField = () => {
  const { t } = useTranslation()
  const bind = useBind<LotFormValue>()
  return <TextArea label={t("Champ libre")} {...bind("free_field")} />
}

export default OriginFields
