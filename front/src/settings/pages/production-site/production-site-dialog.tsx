import { useTranslation } from "react-i18next"

import {
  Biofuel,
  Country,
  Entity,
  Feedstock,
  GESOption,
  ProductionSiteDetails,
} from "common/types"

import * as common from "common/api"
import { Form, useForm } from "common/components/form2"

import {
  normalizeBiofuel,
  normalizeCountry,
  normalizeFeedstock,
} from "common/utils/normalizers"
import { Autocomplete } from "common/components/autocomplete2"

import { Dialog } from "common/components/dialog2"
import { TextInput, Checkbox, RadioGroup } from "common/components/inputs2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { Divider, Grid } from "common/components/scaffold"
import { TagAutocomplete } from "common/components/tag-autocomplete2"
import { useMutation } from "common/hooks/async"
import * as api from "../../api/production-sites"
import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"

interface ProductionSiteFormValue {
  displayInDialog?: boolean
  site_id: string | undefined
  name: string | undefined
  date_mise_en_service: string | undefined
  ges_option: GESOption | undefined
  eligible_dc: boolean
  dc_reference: string | undefined
  address: string | undefined
  city: string | undefined
  postal_code: string | undefined
  country: Country | undefined
  manager_name: string | undefined
  manager_phone: string | undefined
  manager_email: string | undefined
  matieres_premieres: Feedstock[] | undefined
  biocarburants: Biofuel[] | undefined
  certificates: string[] | undefined
}

type ProductionSiteDialogProps = {
  title: string
  description?: string
  productionSite?: ProductionSiteDetails
  readOnly?: boolean
  onClose?: () => void
}

export const ProductionSiteDialog = ({
  title,
  description,
  productionSite,
  readOnly,
  onClose,
}: ProductionSiteDialogProps) => {
  return (
    <Dialog
      onClose={() => onClose && onClose()}
      header={
        <>
          <Dialog.Title>{title}</Dialog.Title>
          <Dialog.Description>{description}</Dialog.Description>
        </>
      }
      size="medium"
    >
      <ProductionSiteForm
        productionSite={productionSite}
        readOnly={readOnly}
        onClose={onClose}
      />
    </Dialog>
  )
}

type ProductionSiteFormDialogProps = {
  productionSite?: ProductionSiteDetails
  readOnly?: boolean
  onClose?: () => void
  description?: string
}

export const ProductionSiteForm = ({
  productionSite,
  readOnly,
  onClose,
  description,
}: ProductionSiteFormDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const notifyError = useNotifyError()

  const addProdSite = useMutation(addProductionSite, {
    invalidates: ["production-sites"],

    onSuccess: () => {
      notify(t("Le site de production a bien été créé !"), {
        variant: "success",
      })
      onClose?.()
    },

    onError: (e) => {
      notifyError(e)
    },
  })

  const updateProdSite = useMutation(updateProductionSite, {
    invalidates: ["production-sites"],

    onSuccess: () => {
      notify(t("Le site de production a bien été modifié !"), {
        variant: "success",
      })
    },

    onError: (e) => {
      notifyError(e)
    },
  })

  const { value, bind } = useForm<ProductionSiteFormValue>({
    site_id: productionSite?.site_siret ?? "",
    name: productionSite?.name ?? "",
    date_mise_en_service: productionSite?.date_mise_en_service ?? "",
    ges_option: productionSite?.ges_option ?? GESOption.Default,

    eligible_dc: productionSite?.eligible_dc ?? false,
    dc_reference: productionSite?.dc_reference ?? "",
    address: productionSite?.address ?? "",
    city: productionSite?.city ?? "",
    postal_code: productionSite?.postal_code ?? "",
    country: productionSite?.country ?? undefined,

    manager_name: productionSite?.manager_name ?? "",
    manager_phone: productionSite?.manager_phone ?? "",
    manager_email: productionSite?.manager_email ?? "",

    matieres_premieres: productionSite?.inputs ?? [],
    biocarburants: productionSite?.outputs ?? [],

    certificates:
      productionSite?.certificates.map((c) => c.certificate_id) ?? [],
  })

  const gesOptions = [
    { value: GESOption.Default, label: t("Valeurs par défaut") },
    { value: GESOption.NUTS2, label: t("Valeurs NUTS2") },
    { value: GESOption.Actual, label: t("Valeurs réelles") },
  ]

  async function submitProductionSite() {
    if (
      !value ||
      !value.country ||
      !value.date_mise_en_service ||
      !value.name
    ) {
      return
    }

    // we add a new one
    if (productionSite === undefined) {
      await addProdSite.execute(entity, value)
    }
    // or we're updating an existing one
    else {
      await updateProdSite.execute(entity, productionSite, value)
    }
  }

  return (
    <>
      {description && (
        <section>
          <p>{description}</p>
        </section>
      )}

      <Form id="production-site" onSubmit={submitProductionSite}>
        <TextInput
          autoFocus
          readOnly={readOnly}
          label={t("Nom du site")}
          {...bind("name")}
          required
        />

        <Grid cols={2} gap="lg">
          <TextInput
            readOnly={readOnly}
            label={t("N° d'identification (SIRET)")}
            {...bind("site_id")}
            required
          />
          <TextInput
            readOnly={readOnly}
            type="date"
            label={t("Date de mise en service")}
            style={{ flex: 1 }}
            {...bind("date_mise_en_service")}
            required
          />
        </Grid>

        <Divider noMargin />

        <TextInput
          readOnly={readOnly}
          label={t("Adresse postale")}
          {...bind("address")}
          required
        />
        <Grid cols={2} gap="lg">
          <TextInput
            readOnly={readOnly}
            label={t("Ville")}
            {...bind("city")}
            required
          />
          <TextInput
            readOnly={readOnly}
            label={t("Code postal")}
            {...bind("postal_code")}
            required
          />
        </Grid>

        <Autocomplete
          readOnly={readOnly}
          label={t("Pays")}
          placeholder={t("Rechercher un pays...")}
          getOptions={common.findCountries}
          normalize={normalizeCountry}
          {...bind("country")}
          required
        />

        <Divider noMargin />

        <TextInput
          readOnly={readOnly}
          label={t("Nom du gérant")}
          {...bind("manager_name")}
          required
        />

        <Grid cols={2} gap="lg">
          <TextInput
            readOnly={readOnly}
            label={t("N° de téléphone du gérant")}
            {...bind("manager_phone")}
            required
          />
          <TextInput
            readOnly={readOnly}
            label={t("Addresse email du gérant")}
            {...bind("manager_email")}
            required
          />
        </Grid>

        <Divider noMargin />

        <Checkbox
          label={t("Éligible double-comptage ?")}
          {...bind("eligible_dc")}
          disabled
        />
        {value.eligible_dc && (
          <TextInput
            label={t("Référence double-comptage")}
            {...bind("dc_reference")}
            disabled
            required
          />
        )}

        <Divider noMargin />

        <RadioGroup
          label={t("Options GES")}
          options={gesOptions}
          {...bind("ges_option")}
          disabled={readOnly}
          required
        />

        <Divider noMargin />

        <TagAutocomplete
          label={t("Matieres premieres")}
          readOnly={readOnly}
          placeholder={t("Ajouter matières premières...")}
          defaultOptions={value.matieres_premieres}
          getOptions={common.findFeedstocks}
          normalize={normalizeFeedstock}
          {...bind("matieres_premieres")}
          required
        />
        <TagAutocomplete
          readOnly={readOnly}
          label={t("Biocarburants")}
          placeholder={t("Ajouter biocarburants...")}
          defaultOptions={value.biocarburants}
          getOptions={common.findBiofuels}
          normalize={normalizeBiofuel}
          {...bind("biocarburants")}
          required
        />

        <Divider noMargin />

        <TagAutocomplete
          readOnly={readOnly}
          label={t("Certificats (2BS, ISCC)")}
          placeholder={t("Rechercher des certificats...")}
          defaultOptions={value.certificates}
          getOptions={(search) => common.findMyCertificates(search, { entity_id: entity.id })} // prettier-ignore
          {...bind("certificates")}
        />
      </Form>
      {!readOnly && (
        <Button
          asideX
          loading={addProdSite.loading || updateProdSite.loading}
          type="submit"
          nativeButtonProps={{
            form: "production-site",
          }}
          iconId="ri-save-line"
          disabled={updateProdSite.loading}
        >
          {t("Sauvegarder")}
        </Button>
      )}
    </>
  )
}

async function addProductionSite(
  entity: Entity,
  form: ProductionSiteFormValue
) {
  const inputs = form.matieres_premieres?.map((mp) => mp.code) ?? []
  const outputs = form.biocarburants?.map((bc) => bc.code) ?? []
  const certificates = form.certificates ?? []

  return api.addProductionSite(
    entity.id,
    form.name!,
    form.date_mise_en_service!,
    form.country!.code_pays,
    form.ges_option!,
    form.site_id!,
    form.address!,
    form.city!,
    form.postal_code!,
    form.eligible_dc,
    form.dc_reference!,
    form.manager_name!,
    form.manager_phone!,
    form.manager_email!,
    inputs,
    outputs,
    certificates
  )
}

async function updateProductionSite(
  entity: Entity,
  psite: ProductionSiteDetails,
  form: ProductionSiteFormValue
) {
  const inputs = form.matieres_premieres?.map((mp) => mp.code) ?? []
  const outputs = form.biocarburants?.map((bc) => bc.code) ?? []
  const certificates = form.certificates ?? []

  return api.updateProductionSite(
    entity.id,
    psite.id,
    form.name!,
    form.date_mise_en_service!,
    form.country!.code_pays,
    form.ges_option!,
    form.site_id!,
    form.address!,
    form.city!,
    form.postal_code!,
    form.eligible_dc,
    form.dc_reference!,
    form.manager_name!,
    form.manager_phone!,
    form.manager_email!,
    inputs,
    outputs,
    certificates
  )
}
