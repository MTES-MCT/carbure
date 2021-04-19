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

type LIP = LabelInputProps
type LACP<T> = LabelAutoCompleteProps<T>
type LRP = LabelProps & Omit<RadioGroupProps, "options">

// make sure we can read the production site before trying to read it
export function isKnown<T>(value: T | string | null): value is T {
  return value !== null && typeof value !== "string"
}

export type FieldsProps = {
  readOnly?: boolean
  data: TransactionFormState
  entity?: EntitySelection
  errors?: Record<string, string>
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

export const Mac = ({ label, ...props }: LRP) => (
  <Label
    label="Il s'agit d'une mise à consommation ?"
    disabled={props.disabled}
    readOnly={props.readOnly}
  >
    <RadioGroup row name="mac" options={macOptions} {...props} />
  </Label>
)

export const Dae = (props: LIP) => (
  <LabelInput
    required
    name="dae"
    label="Numéro douanier (DAE, DAA...)"
    {...props}
  />
)

export const Volume = (props: LIP) => (
  <LabelInput
    required
    name="volume"
    label="Volume en litres (Ethanol à 20°, autres à 15°)"
    type="number"
    {...props}
  />
)

export const Biocarburant = (props: LACP<BC>) => (
  <LabelAutoComplete
    required
    name="biocarburant"
    label="Biocarburant"
    minLength={0}
    getValue={getters.code}
    getLabel={getters.name}
    getQuery={api.findBiocarburants}
    {...props}
  />
)

export const MatierePremiere = (props: LACP<MP>) => (
  <LabelAutoComplete
    required
    name="matiere_premiere"
    label="Matiere premiere"
    minLength={0}
    getValue={getters.code}
    getLabel={getters.name}
    getQuery={api.findMatieresPremieres}
    {...props}
  />
)

export const PaysOrigine = (props: LACP<Country>) => (
  <LabelAutoComplete
    required
    name="pays_origine"
    label="Pays d'origine de la matière première"
    getValue={getters.code_pays}
    getLabel={getters.name}
    getQuery={api.findCountries}
    {...props}
  />
)

export const Producer = (props: LACP<Entity>) => (
  <LabelAutoComplete
    loose
    name="producer"
    label="Producteur"
    getValue={getters.id}
    getLabel={getters.name}
    getQuery={api.findProducers}
    icon={isKnown(props.value) ? UserCheck : undefined}
    {...props}
  />
)

export const ProductionSite = (props: LACP<ProductionSiteDetails>) => (
  <LabelAutoComplete
    loose
    name="production_site"
    label="Site de production"
    minLength={0}
    getValue={getters.id}
    getLabel={getters.name}
    getQuery={api.findProductionSites}
    // icon={isKnown(props.value) ? UserCheck : undefined}
    {...props}
  />
)

export const ProductionSiteCountry = (props: LACP<Country>) => (
  <LabelAutoComplete
    name="production_site_country"
    label="Pays de production"
    getValue={getters.code_pays}
    getLabel={getters.name}
    getQuery={api.findCountries}
    {...props}
  />
)

export const ProductionSiteDate = (props: LIP) => (
  <LabelInput
    required
    name="production_site_date"
    label="Date de mise en service"
    type="date"
    {...props}
  />
)

export const ProductionSiteDblCounting = (props: LIP) => (
  <LabelInput
    name="production_site_dbl_counting"
    label="N° d'enregistrement double-compte"
    {...props}
  />
)

export const ProductionSiteReference = (props: LACP<string>) => (
  <LabelAutoComplete
    name="production_site_reference"
    label="Certificat du site de production"
    minLength={0}
    getValue={getters.raw}
    getLabel={getters.raw}
    getQuery={api.findCertificates}
    {...props}
  />
)

export const CarbureVendor = (props: LACP<Entity>) => (
  <LabelAutoComplete
    name="carbure_vendor"
    label="Fournisseur"
    getValue={getters.id}
    getLabel={getters.name}
    getQuery={api.findEntities}
    icon={isKnown(props.value) ? UserCheck : undefined}
    {...props}
  />
)

export const CarbureSelfCertificate = (props: LACP<string>) => (
  <LabelAutoComplete
    required
    name="carbure_vendor_certificate"
    label="Votre certificat"
    minLength={0}
    getValue={getters.raw}
    getLabel={getters.raw}
    getQuery={api.findCertificates}
    {...props}
  />
)

// readonly version of the above for clients
export const CarbureVendorCertificate = (props: LIP) => (
  <LabelInput
    name="carbure_vendor_certificate"
    label="Certificat du fournisseur"
    {...props}
  />
)

export const UnknownSupplier = (props: LIP) => (
  <LabelInput name="unknown_supplier" label="Fournisseur" {...props} />
)

export const UnknownSupplierCertificate = (props: LACP<string>) => (
  <LabelAutoComplete
    name="unknown_supplier_certificate"
    label="Certificat du fournisseur"
    minLength={0}
    getValue={getters.raw}
    getLabel={getters.raw}
    getQuery={api.findCertificates}
    {...props}
  />
)

export const ChampLibre = (props: LIP) => (
  <LabelInput {...props} name="champ_libre" label="Champ libre" />
)

export const Client = (props: LACP<Entity>) => (
  <LabelAutoComplete
    loose
    name="client"
    label="Client"
    getValue={getters.id}
    getLabel={getters.name}
    getQuery={api.findEntities}
    icon={isKnown(props.value) ? UserCheck : undefined}
    {...props}
  />
)

export const DeliverySite = (props: LACP<DS>) => (
  <LabelAutoComplete
    required
    loose
    name="delivery_site"
    label="Site de livraison"
    getValue={getters.depot_id}
    getLabel={getters.name}
    getQuery={api.findDeliverySites}
    // icon={isKnown(props.value) ? UserCheck : undefined}
    {...props}
  />
)

export const DeliverySiteCountry = (props: LACP<Country>) => (
  <LabelAutoComplete
    required
    name="delivery_site_country"
    label="Pays de livraison"
    getValue={getters.code_pays}
    getLabel={getters.name}
    getQuery={api.findCountries}
    {...props}
  />
)

export const DeliveryDate = (props: LIP) => (
  <LabelInput
    name="delivery_date"
    label="Date de livraison"
    type="date"
    {...props}
  />
)

export const Eec = (props: LIP) => (
  <LabelInput
    name="eec"
    label="EEC"
    type="number"
    step={0.1}
    tooltip="Émissions résultant de l'extraction ou de la culture des matières premières" // prettier-ignore
    {...props}
  />
)

export const El = (props: LIP) => (
  <LabelInput
    name="el"
    label="EL"
    type="number"
    tooltip="Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l'affectation des sols" // prettier-ignore
    step={0.1}
    {...props}
  />
)

export const Ep = (props: LIP) => (
  <LabelInput
    required
    name="ep"
    label="EP"
    type="number"
    tooltip="Émissions résultant de la transformation"
    step={0.1}
    {...props}
  />
)

export const Etd = (props: LIP) => (
  <LabelInput
    required
    name="etd"
    label="ETD"
    type="number"
    tooltip="Émissions résultant du transport et de la distribution"
    step={0.1}
    {...props}
  />
)

export const Eu = (props: LIP) => (
  <LabelInput
    name="eu"
    label="EU"
    type="number"
    tooltip="Émissions résultant du carburant à l'usage"
    step={0.1}
    {...props}
  />
)

export const Esca = (props: LIP) => (
  <LabelInput
    name="esca"
    label="ESCA"
    type="number"
    tooltip="Réductions d'émissions dues à l'accumulation du carbone dans les sols grâce à une meilleure gestion agricole" // prettier-ignore
    step={0.1}
    {...props}
  />
)

export const Eccs = (props: LIP) => (
  <LabelInput
    name="eccs"
    label="ECCS"
    type="number"
    tooltip="Réductions d'émissions dues au piégeage et au stockage géologique du carbone" // prettier-ignore
    step={0.1}
    {...props}
  />
)

export const Eccr = (props: LIP) => (
  <LabelInput
    name="eccr"
    label="ECCR"
    type="number"
    tooltip="Réductions d'émissions dues au piégeage et à la substitution du carbone"
    step={0.1}
    {...props}
  />
)

export const Eee = (props: LIP) => (
  <LabelInput
    name="eee"
    label="EEE"
    type="number"
    tooltip="Réductions d'émissions dues à la production excédentaire d'électricité dans le cadre de la cogénération" // prettier-ignore
    step={0.1}
    {...props}
  />
)

export const GhgTotal = (props: LIP) => (
  <LabelInput
    name="ghg_total"
    label="Total"
    style={{ marginTop: "auto" }}
    {...props}
    readOnly
    value={`${(props.value as number)?.toFixed(2)} gCO2eq/MJ`}
  />
)

export const GhgReduction = (props: LIP) => (
  <LabelInput
    name="ghg_reduction"
    label="Réduction"
    style={{ marginTop: "auto" }}
    {...props}
    readOnly
    value={`${(props.value as number)?.toFixed(2)}%`}
  />
)
