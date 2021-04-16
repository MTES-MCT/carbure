import * as Fields from "./fields"
import { FieldsProps, isKnown } from "./fields"
import { FormGroup } from "common/components/form"

const ProductionFields = ({
  readOnly,
  entity,
  data,
  errors,
  onChange,
}: FieldsProps) => {
  const isLotProducer =
    isKnown(data.producer) && data.producer.id === entity?.id

  const isKnownPsite = isKnown(data.production_site)
  const psiteQueryArgs = isKnown(data.producer) ? [data.producer.id] : []
  const certifQueryArgs = isKnown(data.production_site) ? [null, data.production_site.id] : [] // prettier-ignore

  // values

  const country = isKnown(data.production_site)
    ? data.production_site.country
    : data.production_country

  const dcReference =
    isKnown(data.production_site) && data.matiere_premiere?.is_double_compte
      ? data.production_site.dc_reference ?? ""
      : data.production_site_dbl_counting ?? ""

  const comDate = isKnown(data.production_site)
    ? data.production_site.date_mise_en_service
    : data.production_site_com_date

  // errors

  const psiteError = errors?.carbure_production_site ?? errors?.production_site

  const certifError =
    errors?.carbure_production_site_reference ??
    errors?.unknown_production_site_reference

  return (
    <FormGroup readOnly={readOnly} title="Production" onChange={onChange}>
      <Fields.ProductionSite
        search={isLotProducer}
        value={data.production_site}
        queryArgs={psiteQueryArgs}
        error={psiteError}
      />
      <Fields.ProductionSiteReference
        value={data.production_site_reference ?? ""}
        queryArgs={certifQueryArgs}
        error={certifError}
      />
      <Fields.ProductionSiteCountry
        disabled={isKnownPsite}
        value={country}
        error={errors?.unknown_production_country}
      />
      <Fields.ProductionSiteDblCounting
        disabled={isKnownPsite}
        value={dcReference}
        error={errors?.production_site_dbl_counting}
      />
      <Fields.ProductionSiteDate
        disabled={isKnownPsite}
        value={comDate}
        error={errors?.unknown_production_site_com_date}
      />
    </FormGroup>
  )
}

export default ProductionFields
