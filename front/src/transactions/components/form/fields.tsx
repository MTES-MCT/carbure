import { TFunction, Trans, useTranslation } from "react-i18next"
import cl from "clsx"
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
  CertificateInfo,
  DoubleCountingCertificateInfo
} from "common/types"
import { UserCheck, FileCheck, Return, IconProps } from "common/components/icons"
import { Button } from "common/components/button"
import {
  prompt,
  Dialog,
  DialogTitle,
  DialogButtons,
} from "common/components/dialog"
import styles from "./fields.module.css"
import { formatDate } from "settings/components/common"

function idt<T>(s: T) {
  return s
}

type ContentProps = {
  data?: TransactionFormState
  errors?: Record<string, string>
  t?: TFunction
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
  editable?: boolean
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

const CertificateInfoPrompt = ({
  certificate,
  onResolve,
}: {
  certificate: CertificateInfo | DoubleCountingCertificateInfo
  onResolve: () => void
}) => {
  const { t } = useTranslation()
  return (
    <Dialog onResolve={onResolve} className={styles.certificateDialog}>
      <DialogTitle text={t("Détails du certificat")} />

      <ul className={styles.certificateInfo}>
        <li>
          <b>
            <Trans>ID du certificat</Trans>:{" "}
          </b>
          <span>{certificate.certificate_id}</span>
        </li>
        <li>
          <b>
            <Trans>Société</Trans>:{" "}
          </b>
          <span>{certificate.holder}</span>
        </li>
        {('scope' in certificate) && (
          <li>
            <b>
              <Trans>Périmètre du certificat</Trans>:{" "}
            </b>
            <span>{certificate.scope.join(", ")}</span>
          </li>
        )}
        <li>
          <b>
            <Trans>Période de validité</Trans>:{" "}
          </b>
          <span>
            {formatDate(certificate.valid_from)} →{" "}
            {formatDate(certificate.valid_until)}
          </span>
        </li>
      </ul>

      <DialogButtons>
        <Button icon={Return} onClick={() => onResolve()}>
          <Trans>Retour</Trans>
        </Button>
      </DialogButtons>
    </Dialog>
  )
}

type CertificateIconProps = IconProps & {
  certificate: CertificateInfo | DoubleCountingCertificateInfo
}

const CertificateIcon = ({ certificate, ...props }: CertificateIconProps) => {
  const { t } = useTranslation()

  function openCertificateInfo() {
    prompt((resolve) => (
      <CertificateInfoPrompt certificate={certificate} onResolve={resolve} />
    ))
  }

  return (
    <FileCheck
      {...props}

      title={t("Voir le certificat")}
      onClick={openCertificateInfo}
      onMouseDown={(e: any) => e.stopPropagation()}
      className={cl(props.className, styles.certificateIcon)}
    />
  )
}

export const Mac = ({ label, data, value, t = idt, ...props }: LRP) => {
  const macOptions = [
    { value: "true", label: t("Oui") },
    { value: "false", label: t("Non") },
  ]

  return (
    <Label
      label={t("Il s'agit d'une mise à consommation ?")}
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
}

export const Dae = ({ data, value, errors, t = idt, ...props }: LIP) => (
  <LabelInput
    required
    name="dae"
    label={t("Numéro douanier (DAE, DAA...)")}
    value={value ?? data?.dae}
    error={errors?.dae}
    {...props}
  />
)

export const Volume = ({ data, value, errors, t = idt, ...props }: LIP) => (
  <LabelInput
    required
    name="volume"
    label={t("Volume en litres (Ethanol à 20°, autres à 15°)")}
    type="number"
    value={value ?? data?.volume}
    error={errors?.volume}
    {...props}
  />
)

export const Biocarburant = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LACP<BC>) => {
  return (
    <LabelAutoComplete
      required
      name="biocarburant"
      label={t("Biocarburant")}
      minLength={0}
      value={value ?? data?.biocarburant}
      error={errors?.biocarburant_code}
      getValue={getters.code}
      getLabel={(bc) => t(bc.code, { ns: "biofuels" })}
      getQuery={api.findBiocarburants}
      {...props}
    />
  )
}

export const MatierePremiere = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LACP<MP>) => {
  const category = data?.matiere_premiere?.category

  return (
    <LabelAutoComplete
      required
      name="matiere_premiere"
      label={t("Matière première")}
      minLength={0}
      value={value ?? data?.matiere_premiere ?? null}
      error={errors?.matiere_premiere_code}
      getValue={getters.code}
      getLabel={(mp) => t(mp.code, { ns: "feedstocks" })}
      getQuery={api.findMatieresPremieres}
      icon={(p: any) => <span {...p}>{category}</span>}
      {...props}
    />
  )
}

export const PaysOrigine = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LACP<Country>) => (
  <LabelAutoComplete
    required
    name="pays_origine"
    label={t("Pays d'origine de la matière première")}
    value={value ?? data?.pays_origine ?? null}
    error={errors?.pays_origine_code}
    getValue={getters.code_pays}
    getLabel={(c) => t(c.code_pays, { ns: "countries" })}
    getQuery={api.findCountries}
    {...props}
  />
)

export const Producer = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LACP<Entity>) => {
  const producer = value ?? data?.producer ?? null
  const error = errors?.carbure_producer ?? errors?.producer

  // prettier-ignore
  const icon = isKnown(producer)
    ? (props: any) => <UserCheck {...props} title={t("Ce producteur est enregistré sur CarbuRe")} />
    : undefined

  return (
    <LabelAutoComplete
      loose
      name="producer"
      label={t("Producteur")}
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
  t = idt,
  ...props
}: LACP<ProductionSiteDetails>) => {
  const psite = value ?? data?.production_site
  const error = errors?.carbure_production_site ?? errors?.production_site

  // prettier-ignore
  const icon = isKnown(psite)
    ? (props: any) => <UserCheck {...props} title={t("Ce site de production est enregistré sur CarbuRe")} />
    : undefined

  return (
    <LabelAutoComplete
      loose
      name="production_site"
      label={t("Site de production")}
      minLength={0}
      value={psite}
      error={error}
      getValue={getters.id}
      getLabel={getters.name}
      getQuery={api.findProductionSites}
      icon={icon}
      {...props}
    />
  )
}

export const ProductionSiteCountry = ({
  data,
  value,
  errors,
  t = idt,
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
      label={t("Pays de production")}
      value={value ?? country}
      error={errors?.unknown_production_country}
      getValue={getters.code_pays}
      getLabel={(c) => t(c.code_pays, { ns: "countries" })}
      getQuery={api.findCountries}
      {...props}
    />
  )
}

export const ProductionSiteDate = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LIP) => {
  const comDate =
    data && isKnown(data.production_site)
      ? data.production_site.date_mise_en_service
      : data?.production_site_com_date

  return (
    <LabelInput
      required
      disabled={isKnown(data?.production_site)}
      name="production_site_com_date"
      label={t("Date de mise en service")}
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
  icon:forcedIcon,
  t = idt,
  ...props
}: LIP) => {
  const hasDC = Boolean(data?.matiere_premiere?.is_double_compte)
  const dcReference = value ?? data?.production_site_dbl_counting ?? ""

  const certInfo = data?.certificates?.double_counting_reference ?? data?.certificates?.unknown_production_site_dbl_counting
  const isKnownCert = Boolean(certInfo) && certInfo?.found

  const icon = forcedIcon ?? isKnownCert
    ? (p: any) => <CertificateIcon {...p} certificate={certInfo} />
    : undefined

  return (
    <LabelInput
      disabled={isKnown(data?.production_site) || !hasDC}
      name="production_site_dbl_counting"
      label={t("N° d'enregistrement double-compte")}
      value={hasDC ? dcReference : ""}
      error={errors?.production_site_dbl_counting}
      icon={icon}
      {...props}
    />
  )
}

export const ProductionSiteReference = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LACP<string>) => {
  const queryArgs = data && isKnown(data.production_site) ? [null, data.production_site.id] : [] // prettier-ignore
  const error = errors?.carbure_production_site_reference ?? errors?.unknown_production_site_reference // prettier-ignore

  const certInfo = data?.certificates?.production_site_certificate
  const isKnownCert = Boolean(certInfo) && certInfo?.found

  const icon = isKnownCert
    ? (p: any) => <CertificateIcon {...p} certificate={certInfo} />
    : undefined

  const cert = isKnownCert
    ? certInfo?.certificate_id
    : data?.production_site_reference

  return (
    <LabelAutoComplete
      loose
      name="production_site_reference"
      label={t("Certificat du site de production")}
      minLength={0}
      value={value ?? cert}
      icon={icon}
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
  t = idt,
  ...props
}: LACP<Entity>) => {
  const vendor = value ?? data?.carbure_vendor

  // prettier-ignore
  const icon = isKnown(vendor)
    ? (props: any) => <UserCheck {...props} title={t("Ce fournisseur est enregistré sur CarbuRe")} />
    : undefined

  return (
    <LabelAutoComplete
      name="carbure_vendor"
      label={t("Fournisseur")}
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
  t = idt,
  ...props
}: LACP<string>) => {
  const certInfo = data?.certificates?.vendor_certificate
  const isKnownCert = Boolean(certInfo) && certInfo?.found

  const icon = isKnownCert
    ? (p: any) => <CertificateIcon {...p} certificate={certInfo} />
    : undefined

  const cert = isKnownCert
    ? certInfo?.certificate_id
    : data?.carbure_vendor_certificate

  return (
    <LabelAutoComplete
      loose
      required
      name="carbure_vendor_certificate"
      label={t("Votre certificat")}
      minLength={0}
      value={value ?? cert}
      icon={icon}
      error={errors?.carbure_vendor_certificate}
      queryArgs={[data?.carbure_vendor?.id]}
      getValue={getters.raw}
      getLabel={getters.raw}
      getQuery={api.findCertificates}
      {...props}
    />
  )
}

// readonly version of the above for clients
export const CarbureVendorCertificate = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LACP<string>) => {
  const certInfo = data?.certificates?.vendor_certificate
  const isKnownCert = Boolean(certInfo) && certInfo?.found

  const icon = isKnownCert
    ? (p: any) => <CertificateIcon {...p} certificate={certInfo} />
    : undefined

  const cert = isKnownCert
    ? certInfo?.certificate_id
    : data?.carbure_vendor_certificate

  return (
    <LabelAutoComplete
      search={false}
      name="carbure_vendor_certificate"
      label={t("Certificat du fournisseur")}
      value={value ?? cert}
      icon={icon}
      error={errors?.carbure_vendor_certificate}
      {...props}
    />
  )
}

export const UnknownSupplier = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LIP) => (
  <LabelInput
    disabled={isKnown(data?.producer)}
    name="unknown_supplier"
    label={t("Fournisseur")}
    value={value ?? data?.unknown_supplier ?? ""}
    error={errors?.unknown_supplier}
    {...props}
  />
)

export const UnknownSupplierCertificate = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LACP<string>) => {
  const certInfo = data?.certificates?.supplier_certificate
  const isKnownCert = Boolean(certInfo) && certInfo?.found

  const icon = isKnownCert
    ? (p: any) => <CertificateIcon {...p} certificate={certInfo} />
    : undefined

  const cert = isKnownCert
    ? certInfo?.certificate_id
    : data?.unknown_supplier_certificate

  return (
    <LabelAutoComplete
      loose
      disabled={isKnown(data?.producer)}
      name="unknown_supplier_certificate"
      label={t("Certificat du fournisseur")}
      minLength={0}
      value={value ?? cert}
      icon={icon}
      error={errors?.unknown_supplier_certificate}
      getValue={getters.raw}
      getLabel={getters.raw}
      getQuery={api.findCertificates}
      {...props}
    />
  )
}

export const ChampLibre = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LTAP) => (
  <LabelTextArea
    name="champ_libre"
    label={t("Champ libre")}
    value={value ?? data?.champ_libre}
    {...props}
  />
)

export const Client = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LACP<Entity>) => {
  const client = value ?? data?.client

  // prettier-ignore
  const icon = isKnown(client)
    ? (props: any) => <UserCheck {...props} title={t("Ce client est enregistré sur CarbuRe")} />
    : undefined

  return (
    <LabelAutoComplete
      loose
      name="client"
      label={t("Client")}
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

export const DeliverySite = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LACP<DS>) => {
  const depot = value ?? data?.delivery_site
  const distance = data?.distance?.distance
  const gmaps = data?.distance?.link

  const labelText = t("Site de livraison")

  const label: React.ReactNode =
    typeof distance === "number" && distance > 0 ? (
      <>
        {labelText}{" "}
        <a
          href={gmaps}
          target="_blank"
          className={styles.distanceLink}
          rel="noreferrer"
        >
          ({distance}km)
        </a>
      </>
    ) : (
      labelText
    )

  // prettier-ignore
  const icon = isKnown(depot)
    ? (props: any) => <UserCheck {...props} title={t("Ce site de livraison est enregistré sur CarbuRe")} />
    : undefined

  return (
    <LabelAutoComplete
      loose
      required
      disabled={data?.mac}
      name="delivery_site"
      label={label}
      tooltip={labelText}
      value={depot}
      error={errors?.delivery_site ?? errors?.unknown_delivery_site}
      getValue={getters.depot_id}
      getLabel={getters.name}
      getQuery={api.findDeliverySites}
      icon={icon}
      {...props}
    />
  )
}

export const DeliverySiteCountry = ({
  data,
  value,
  errors,
  t = idt,
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
      label={t("Pays de livraison")}
      value={value ?? dsCountry}
      error={errors?.unknown_delivery_site_country}
      getValue={getters.code_pays}
      getLabel={(c) => t(c.code_pays, { ns: "countries" })}
      getQuery={api.findCountries}
      {...props}
    />
  )
}

export const DeliveryDate = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LIP) => (
  <LabelInput
    name="delivery_date"
    label={t("Date de livraison")}
    type="date"
    value={value ?? data?.delivery_date}
    error={errors?.delivery_date}
    {...props}
  />
)

export const Eec = ({ data, value, errors, t = idt, ...props }: LIP) => (
  <LabelInput
    name="eec"
    label={t("EEC")}
    type="number"
    step={0.1}
    tooltip={t("Émissions résultant de l'extraction ou de la culture des matières premières")} // prettier-ignore
    value={value ?? data?.eec}
    error={errors?.eec}
    {...props}
  />
)

export const El = ({ data, value, errors, t = idt, ...props }: LIP) => (
  <LabelInput
    name="el"
    label={t("EL")}
    type="number"
    tooltip={t("Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l'affectation des sols")} // prettier-ignore
    step={0.1}
    value={value ?? data?.el}
    error={errors?.el}
    {...props}
  />
)

export const Ep = ({ data, value, errors, t = idt, ...props }: LIP) => (
  <LabelInput
    required
    name="ep"
    label={t("EP")}
    type="number"
    tooltip={t("Émissions résultant dela transformation")}
    step={0.1}
    value={value ?? data?.ep}
    error={errors?.ep}
    {...props}
  />
)

export const Etd = ({ data, value, errors, t = idt, ...props }: LIP) => (
  <LabelInput
    required
    name="etd"
    label={t("ETD")}
    type="number"
    tooltip={t("Émissions résultant du transport et de la distribution")}
    step={0.1}
    value={value ?? data?.etd}
    error={errors?.etd}
    {...props}
  />
)

export const Eu = ({ data, value, errors, t = idt, ...props }: LIP) => (
  <LabelInput
    name="eu"
    label={t("EU")}
    type="number"
    tooltip={t("Émissions résultant du carburant à l'usage")}
    step={0.1}
    value={value ?? data?.eu}
    error={errors?.eu}
    {...props}
  />
)

export const Esca = ({ data, value, errors, t = idt, ...props }: LIP) => (
  <LabelInput
    name="esca"
    label={t("ESCA")}
    type="number"
    tooltip={t("Réductions d'émissions dues à l'accumulation du carbone dans les sols grâce à une meilleure gestion agricole")} // prettier-ignore
    step={0.1}
    value={value ?? data?.esca}
    error={errors?.esca}
    {...props}
  />
)

export const Eccs = ({ data, value, errors, t = idt, ...props }: LIP) => (
  <LabelInput
    name="eccs"
    label={t("ECCS")}
    type="number"
    tooltip={t("Réductions d'émissions dues au piégeage et au stockage géologique du carbone")} // prettier-ignore
    step={0.1}
    value={value ?? data?.eccs}
    error={errors?.eccs}
    {...props}
  />
)

export const Eccr = ({ data, value, errors, t = idt, ...props }: LIP) => (
  <LabelInput
    name="eccr"
    label={t("ECCR")}
    type="number"
    tooltip={t(
      "Réductions d'émissions dues au piégeage et à la substitution du carbone"
    )}
    step={0.1}
    value={value ?? data?.eccr}
    error={errors?.eccr}
    {...props}
  />
)

export const Eee = ({ data, value, errors, t = idt, ...props }: LIP) => (
  <LabelInput
    name="eee"
    label={t("EEE")}
    type="number"
    tooltip={t("Réductions d'émissions dues à la production excédentaire d'électricité dans le cadre de la cogénération")} // prettier-ignore
    step={0.1}
    value={value ?? data?.eee}
    error={errors?.eee}
    {...props}
  />
)

export const GhgTotal = ({ data, value, errors, t = idt, ...props }: LIP) => {
  const total = (value as number) ?? data?.ghg_total ?? 0
  return (
    <LabelInput
      name="ghg_total"
      label={t("Total")}
      style={{ marginTop: "auto" }}
      {...props}
      readOnly
      value={`${total.toFixed(2)} gCO2eq/MJ`}
    />
  )
}

export const GhgReduction = ({
  data,
  value,
  errors,
  t = idt,
  ...props
}: LIP) => {
  const reduction = (value as number) ?? data?.ghg_reduction ?? 0
  return (
    <LabelInput
      name="ghg_reduction"
      label={t("Réduction")}
      style={{ marginTop: "auto" }}
      {...props}
      readOnly
      value={`${reduction.toFixed(2)}%`}
    />
  )
}
