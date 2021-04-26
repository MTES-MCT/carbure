import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionFormState } from "transactions/hooks/use-transaction-form"
import * as api from "common/api"
import {
  LabelAutoComplete,
  LabelAutoCompleteProps,
} from "common/components/autocomplete"
import {
  Label,
  LabelInput,
  LabelInputProps,
  LabelProps,
  LabelTextArea,
  LabelTextAreaProps,
} from "common/components/input"
import RadioGroup, { RadioGroupProps } from "common/components/radio-group"
import { FormChangeHandler } from "common/hooks/use-form"
import {
  Biocarburant as BC,
  Country,
  DeliverySite as DS,
  Entity,
  MatierePremiere as MP,
  ProductionSiteDetails,
} from "common/types"
import { UserCheck } from "common/components/icons"

type ContentProps = {
  data?: TransactionFormState
  errors?: Record<string, string>
}

type LIP = LabelInputProps & ContentProps
type LACP<T> = LabelAutoCompleteProps<T> & ContentProps
type LRP = LabelProps & Omit<RadioGroupProps, "options"> & ContentProps
type LTAP = LabelTextAreaProps & ContentProps

// make sure we can read the production site before trying to read it
export function isKnown<T>(value: T | string | undefined | null): value is T {
  return value !== null && typeof value !== 'undefined' && typeof value !== "string" // prettier-ignore
}

export type FieldsProps = {
  disabled?: boolean
  readOnly?: boolean
  stock?: boolean
  data: TransactionFormState
  errors: Record<string, string>
  entity?: EntitySelection
  onChange: FormChangeHandler<TransactionFormState>
}

// shorthand to build autocomplete value & label getters
const get = (key: string) => (obj: { [k: string]: any } | null) =>
  obj && key in obj ? String(obj[key]) : ""

const getters = {
  code: get("code"),
  name: get("name"),
  code_pays: get("code_pays"),
  id: get("id"),
  depot_id: get("depot_id"),
  raw: (v: string) => v,
}

const macOptions = [
  { value: "true", label: "Oui" },
  { value: "false", label: "Non" },
]

export const Mac = ({ label, data, value, ...props }: LRP) => (
  <Label
    label="Il s'agit d'une mise à consommation ?"
    disabled={props.disabled}
    readOnly={props.readOnly}
  >
    <RadioGroup
      row
      name="mac"
      options={macOptions}
      value={value ?? `${data?.mac ?? ""}`}
      {...props}
    />
  </Label>
)

export const Dae = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    required
    name="dae"
    label="Numéro douanier (DAE, DAA...)"
    value={value ?? data?.dae}
    error={errors?.dae}
    {...props}
  />
)

export const Volume = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    required
    name="volume"
    label="Volume en litres (Ethanol à 20°, autres à 15°)"
    type="number"
    value={value ?? data?.volume}
    error={errors?.volume}
    {...props}
  />
)

export const Biocarburant = ({ data, value, errors, ...props }: LACP<BC>) => (
  <LabelAutoComplete
    required
    name="biocarburant"
    label="Biocarburant"
    minLength={0}
    value={value ?? data?.biocarburant ?? null}
    error={errors?.biocarburant_code}
    getValue={getters.code}
    getLabel={getters.name}
    getQuery={api.findBiocarburants}
    {...props}
  />
)

export const MatierePremiere = ({
  data,
  value,
  errors,
  ...props
}: LACP<MP>) => (
  <LabelAutoComplete
    required
    name="matiere_premiere"
    label="Matiere premiere"
    minLength={0}
    value={value ?? data?.matiere_premiere ?? null}
    error={errors?.matiere_premiere_code}
    getValue={getters.code}
    getLabel={getters.name}
    getQuery={api.findMatieresPremieres}
    {...props}
  />
)

export const PaysOrigine = ({
  data,
  value,
  errors,
  ...props
}: LACP<Country>) => (
  <LabelAutoComplete
    required
    name="pays_origine"
    label="Pays d'origine de la matière première"
    value={value ?? data?.pays_origine ?? null}
    error={errors?.pays_origine_code}
    getValue={getters.code_pays}
    getLabel={getters.name}
    getQuery={api.findCountries}
    {...props}
  />
)

export const Producer = ({ data, value, errors, ...props }: LACP<Entity>) => {
  const producer = value ?? data?.producer ?? null
  const error = errors?.carbure_producer ?? errors?.producer

  // prettier-ignore
  const icon = isKnown(producer)
    ? (props: any) => <UserCheck {...props} title="Ce producteur est enregistré dans CarbuRe" />
    : undefined

  return (
    <LabelAutoComplete
      loose
      name="producer"
      label="Producteur"
      minLength={0}
      value={producer}
      error={error}
      getValue={getters.id}
      getLabel={getters.name}
      getQuery={api.findProducers}
      icon={icon}
      {...props}
    />
  )
}

export const ProductionSite = ({
  data,
  value,
  errors,
  ...props
}: LACP<ProductionSiteDetails>) => {
  const queryArgs = data && isKnown(data.producer) ? [data.producer.id] : []
  const error = errors?.carbure_production_site ?? errors?.production_site

  return (
    <LabelAutoComplete
      loose
      name="production_site"
      label="Site de production"
      minLength={0}
      value={value ?? data?.production_site}
      error={error}
      getValue={getters.id}
      getLabel={getters.name}
      getQuery={api.findProductionSites}
      queryArgs={queryArgs}
      {...props}
    />
  )
}

export const ProductionSiteCountry = ({
  data,
  value,
  errors,
  ...props
}: LACP<Country>) => {
  const country =
    data && isKnown(data.production_site)
      ? data.production_site.country
      : data?.production_site_country

  return (
    <LabelAutoComplete
      disabled={isKnown(data?.production_site)}
      name="production_site_country"
      label="Pays de production"
      value={value ?? country}
      error={errors?.unknown_production_country}
      getValue={getters.code_pays}
      getLabel={getters.name}
      getQuery={api.findCountries}
      {...props}
    />
  )
}

export const ProductionSiteDate = ({ data, value, errors, ...props }: LIP) => {
  const comDate =
    data && isKnown(data.production_site)
      ? data.production_site.date_mise_en_service
      : data?.production_site_com_date

  return (
    <LabelInput
      required
      disabled={isKnown(data?.production_site)}
      name="production_site_com_date"
      label="Date de mise en service"
      type="date"
      value={comDate}
      error={errors?.unknown_production_site_com_date}
      {...props}
    />
  )
}

export const ProductionSiteDblCounting = ({
  data,
  value,
  errors,
  ...props
}: LIP) => {
  const dcReference =
    data &&
    isKnown(data.production_site) &&
    data.matiere_premiere?.is_double_compte
      ? data.production_site.dc_reference ?? ""
      : data?.production_site_dbl_counting ?? ""

  return (
    <LabelInput
      disabled={isKnown(data?.production_site)}
      name="production_site_dbl_counting"
      label="N° d'enregistrement double-compte"
      value={value ?? dcReference}
      error={errors?.production_site_dbl_counting}
      {...props}
    />
  )
}

export const ProductionSiteReference = ({
  data,
  value,
  errors,
  ...props
}: LACP<string>) => {
  const queryArgs = data && isKnown(data.production_site) ? [null, data.production_site.id] : [] // prettier-ignore
  const error = errors?.carbure_production_site_reference ?? errors?.unknown_production_site_reference // prettier-ignore

  return (
    <LabelAutoComplete
      loose
      name="production_site_reference"
      label="Certificat du site de production"
      minLength={0}
      value={value ?? data?.production_site_reference}
      error={error}
      queryArgs={queryArgs}
      getValue={getters.raw}
      getLabel={getters.raw}
      getQuery={api.findCertificates}
      {...props}
    />
  )
}

export const CarbureVendor = ({
  data,
  value,
  errors,
  ...props
}: LACP<Entity>) => {
  const vendor = value ?? data?.carbure_vendor

  // prettier-ignore
  const icon = isKnown(vendor)
    ? (props: any) => <UserCheck {...props} title="Ce fournisseur est enregistré dans CarbuRe" />
    : undefined

  return (
    <LabelAutoComplete
      name="carbure_vendor"
      label="Fournisseur"
      value={vendor}
      error={errors?.carbure_vendor}
      getValue={getters.id}
      getLabel={getters.name}
      getQuery={api.findEntities}
      icon={icon}
      {...props}
    />
  )
}

export const CarbureSelfCertificate = ({
  data,
  value,
  errors,
  ...props
}: LACP<string>) => (
  <LabelAutoComplete
    loose
    required
    name="carbure_vendor_certificate"
    label="Votre certificat"
    minLength={0}
    value={value ?? data?.carbure_vendor_certificate}
    error={errors?.carbure_vendor_certificate}
    queryArgs={[data?.carbure_vendor?.id]}
    getValue={getters.raw}
    getLabel={getters.raw}
    getQuery={api.findCertificates}
    {...props}
  />
)

// readonly version of the above for clients
export const CarbureVendorCertificate = ({
  data,
  value,
  errors,
  ...props
}: LIP) => (
  <LabelInput
    name="carbure_vendor_certificate"
    label="Certificat du fournisseur"
    value={value ?? data?.carbure_vendor_certificate}
    error={errors?.carbure_vendor_certificate}
    {...props}
  />
)

export const UnknownSupplier = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    disabled={isKnown(data?.producer)}
    name="unknown_supplier"
    label="Fournisseur"
    value={value ?? data?.unknown_supplier ?? ""}
    error={errors?.unknown_supplier}
    {...props}
  />
)

export const UnknownSupplierCertificate = ({
  data,
  value,
  errors,
  ...props
}: LACP<string>) => (
  <LabelAutoComplete
    loose
    disabled={isKnown(data?.producer)}
    name="unknown_supplier_certificate"
    label="Certificat du fournisseur"
    minLength={0}
    value={value ?? data?.unknown_supplier_certificate}
    error={errors?.unknown_supplier_certificate}
    getValue={getters.raw}
    getLabel={getters.raw}
    getQuery={api.findCertificates}
    {...props}
  />
)

export const ChampLibre = ({ data, value, errors, ...props }: LTAP) => (
  <LabelTextArea
    name="champ_libre"
    label="Champ libre"
    value={value ?? data?.champ_libre}
    {...props}
  />
)

export const Client = ({ data, value, errors, ...props }: LACP<Entity>) => {
  const client = value ?? data?.client

  // prettier-ignore
  const icon = isKnown(client)
    ? (props: any) => <UserCheck {...props} title="Ce client est enregistré dans CarbuRe" />
    : undefined

  return (
    <LabelAutoComplete
      loose
      name="client"
      label="Client"
      value={client}
      error={errors?.client}
      getValue={getters.id}
      getLabel={getters.name}
      getQuery={api.findEntities}
      icon={icon}
      {...props}
    />
  )
}

export const DeliverySite = ({ data, value, errors, ...props }: LACP<DS>) => (
  <LabelAutoComplete
    loose
    required
    disabled={data?.mac}
    name="delivery_site"
    label="Site de livraison"
    value={value ?? data?.delivery_site}
    error={errors?.delivery_site}
    getValue={getters.depot_id}
    getLabel={getters.name}
    getQuery={api.findDeliverySites}
    {...props}
  />
)

export const DeliverySiteCountry = ({
  data,
  value,
  errors,
  ...props
}: LACP<Country>) => {
  const disabled = isKnown(data?.delivery_site) || data?.mac

  const dsCountry =
    data && isKnown(data.delivery_site)
      ? data.delivery_site.country
      : data?.delivery_site_country

  return (
    <LabelAutoComplete
      required
      disabled={disabled}
      name="delivery_site_country"
      label="Pays de livraison"
      value={value ?? dsCountry}
      error={errors?.unknown_delivery_site_country}
      getValue={getters.code_pays}
      getLabel={getters.name}
      getQuery={api.findCountries}
      {...props}
    />
  )
}

export const DeliveryDate = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    name="delivery_date"
    label="Date de livraison"
    type="date"
    value={value ?? data?.delivery_date}
    error={errors?.delivery_date}
    {...props}
  />
)

export const Eec = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    name="eec"
    label="EEC"
    type="number"
    step={0.1}
    tooltip="Émissions résultant de l'extraction ou de la culture des matières premières" // prettier-ignore
    value={value ?? data?.eec}
    error={errors?.eec}
    {...props}
  />
)

export const El = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    name="el"
    label="EL"
    type="number"
    tooltip="Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l'affectation des sols" // prettier-ignore
    step={0.1}
    value={value ?? data?.el}
    error={errors?.el}
    {...props}
  />
)

export const Ep = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    required
    name="ep"
    label="EP"
    type="number"
    tooltip="Émissions résultant de la transformation"
    step={0.1}
    value={value ?? data?.ep}
    error={errors?.ep}
    {...props}
  />
)

export const Etd = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    required
    name="etd"
    label="ETD"
    type="number"
    tooltip="Émissions résultant du transport et de la distribution"
    step={0.1}
    value={value ?? data?.etd}
    error={errors?.etd}
    {...props}
  />
)

export const Eu = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    name="eu"
    label="EU"
    type="number"
    tooltip="Émissions résultant du carburant à l'usage"
    step={0.1}
    value={value ?? data?.eu}
    error={errors?.eu}
    {...props}
  />
)

export const Esca = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    name="esca"
    label="ESCA"
    type="number"
    tooltip="Réductions d'émissions dues à l'accumulation du carbone dans les sols grâce à une meilleure gestion agricole" // prettier-ignore
    step={0.1}
    value={value ?? data?.esca}
    error={errors?.esca}
    {...props}
  />
)

export const Eccs = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    name="eccs"
    label="ECCS"
    type="number"
    tooltip="Réductions d'émissions dues au piégeage et au stockage géologique du carbone" // prettier-ignore
    step={0.1}
    value={value ?? data?.eccs}
    error={errors?.eccs}
    {...props}
  />
)

export const Eccr = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    name="eccr"
    label="ECCR"
    type="number"
    tooltip="Réductions d'émissions dues au piégeage et à la substitution du carbone"
    step={0.1}
    value={value ?? data?.eccr}
    error={errors?.eccr}
    {...props}
  />
)

export const Eee = ({ data, value, errors, ...props }: LIP) => (
  <LabelInput
    name="eee"
    label="EEE"
    type="number"
    tooltip="Réductions d'émissions dues à la production excédentaire d'électricité dans le cadre de la cogénération" // prettier-ignore
    step={0.1}
    value={value ?? data?.eee}
    error={errors?.eee}
    {...props}
  />
)

export const GhgTotal = ({ data, value, errors, ...props }: LIP) => {
  const total = (value as number) ?? data?.ghg_total ?? 0
  return (
    <LabelInput
      name="ghg_total"
      label="Total"
      style={{ marginTop: "auto" }}
      {...props}
      readOnly
      value={`${total.toFixed(2)} gCO2eq/MJ`}
    />
  )
}

export const GhgReduction = ({ data, value, errors, ...props }: LIP) => {
  const reduction = (value as number) ?? data?.ghg_reduction ?? 0
  return (
    <LabelInput
      name="ghg_reduction"
      label="Réduction"
      style={{ marginTop: "auto" }}
      {...props}
      readOnly
      value={`${reduction.toFixed(2)}%`}
    />
  )
}
