import { Trans, useTranslation } from "react-i18next"

import {
  Biofuel,
  Country,
  Entity,
  Feedstock,
  GESOption,
  ProductionSiteDetails,
} from "common/types"

import * as common from "common/api"
import Form, { useForm } from "common/components/form"

import {
  normalizeBiofuel,
  normalizeCountry,
  normalizeFeedstock,
} from "common/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import Button from "common/components/button"
import Checkbox from "common/components/checkbox"
import Dialog from "common/components/dialog"
import { Return, Save } from "common/components/icons"
import { TextInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { RadioGroup } from "common/components/radio"
import { Row } from "common/components/scaffold"
import TagAutocomplete from "common/components/tag-autocomplete"
import { useMutation } from "common/hooks/async"
import * as api from "../api/production-sites"
import useEntity from "common/hooks/entity"

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
  displayFormOnly?: boolean
}

export const ProductionSiteDialog = ({
  title,
  description,
  productionSite,
  readOnly,
  onClose,
  displayFormOnly,
}: ProductionSiteDialogProps) => {
  return (
    <Dialog onClose={() => onClose && onClose()}>
      {!displayFormOnly && (
        <header>
          <h1>{title}</h1>
        </header>
      )}

      <ProductionSiteForm
        productionSite={productionSite}
        readOnly={readOnly}
        onClose={onClose}
        description={description}
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
  const addProdSite = useMutation(addProductionSite, {
    invalidates: ["production-sites"],

    onSuccess: () => {
      notify(t("Le site de production a bien été créé !"), {
        variant: "success",
      })
      onClose?.()
    },

    onError: () => {
      notify(t("Impossible de créer le site de production."), {
        variant: "danger",
      })
    },
  })

  const updateProdSite = useMutation(updateProductionSite, {
    invalidates: ["production-sites"],

    onSuccess: () => {
      notify(t("Le site de production a bien été modifié !"), {
        variant: "success",
      })
    },

    onError: () => {
      notify(t("Impossible de modifier le site de production."), {
        variant: "danger",
      })
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
      <main>
        {description && (
          <section>
            <p>{description}</p>
          </section>
        )}

        <section>
          <Form id="production-site" onSubmit={submitProductionSite}>
            <TextInput
              autoFocus
              readOnly={readOnly}
              label={t("Nom du site")}
              {...bind("name")}
              required
            />

            <Row style={{ gap: "var(--spacing-m)" }}>
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
            </Row>

            <hr />

            <TextInput
              readOnly={readOnly}
              label={t("Adresse postale")}
              {...bind("address")}
              required
            />
            <Row style={{ gap: "var(--spacing-m)" }}>
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
            </Row>

            <Autocomplete
              readOnly={readOnly}
              label={t("Pays")}
              placeholder={t("Rechercher un pays...")}
              getOptions={common.findCountries}
              normalize={normalizeCountry}
              {...bind("country")}
              required
            />

            <hr />

            <TextInput
              readOnly={readOnly}
              label={t("Nom du gérant")}
              {...bind("manager_name")}
              required
            />

            <Row style={{ gap: "var(--spacing-m)" }}>
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
            </Row>

            <hr />

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

            <hr />

            <RadioGroup
              label={t("Options GES")}
              options={gesOptions}
              {...bind("ges_option")}
              disabled={readOnly}
              required
            />

            <hr />

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

            <hr />

            <TagAutocomplete
              readOnly={readOnly}
              label={t("Certificats (2BS, ISCC)")}
              placeholder={t("Rechercher des certificats...")}
              defaultOptions={value.certificates}
              getOptions={(search) => common.findMyCertificates(search, { entity_id: entity.id })} // prettier-ignore
              {...bind("certificates")}
              required
            />
          </Form>
        </section>
      </main>

      <footer>
        {!readOnly && (
          <Button
            asideX
            loading={addProdSite.loading || updateProdSite.loading}
            variant="primary"
            submit="production-site"
            icon={Save}
            disabled={updateProdSite.loading}
            label={t("Sauvegarder")}
          />
        )}
        {onClose && (
          <Button asideX={readOnly} icon={Return} action={onClose}>
            <Trans>Retour</Trans>
          </Button>
        )}
      </footer>
    </>
  )
}

async function addProductionSite(
  entity: Entity,
  form: ProductionSiteFormValue
) {
  const res = await api.addProductionSite(
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
    form.manager_email!
  )

  const psite = res.data!

  const mps = form.matieres_premieres?.map((mp) => mp.code)
  await api.setProductionSiteFeedstock(entity.id, psite!.id, mps ?? [])

  const bcs = form.biocarburants?.map((bc) => bc.code)
  await api.setProductionSiteBiofuel(entity.id, psite!.id, bcs ?? [])

  const cs = form.certificates ?? []
  await api.setProductionSiteCertificates(entity.id, psite!.id, cs)
}

async function updateProductionSite(
  entity: Entity,
  psite: ProductionSiteDetails,
  form: ProductionSiteFormValue
) {
  await api.updateProductionSite(
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
    form.manager_email!
  )

  const mps = form.matieres_premieres?.map((mp) => mp.code)
  await api.setProductionSiteFeedstock(entity.id, psite!.id, mps ?? [])

  const bcs = form.biocarburants?.map((bc) => bc.code)
  await api.setProductionSiteBiofuel(entity.id, psite!.id, bcs ?? [])

  const cs = form.certificates ?? []
  await api.setProductionSiteCertificates(entity.id, psite!.id, cs)
}
