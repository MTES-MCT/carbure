import { Trans, useTranslation } from "react-i18next"

import { Entity, UserRole } from "carbure/types"
import {
  Biofuel,
  Country,
  Feedstock,
  GESOption,
  ProductionSiteDetails,
} from "common-v2/types"

import * as common from "common-v2/api"
import Form, { useForm } from "common-v2/components/form"

import { Row, LoaderOverlay } from "common-v2/components/scaffold"
import { TextInput } from "common-v2/components/input"
import Checkbox from "common-v2/components/checkbox"
import Button from "common-v2/components/button"
import {
  AlertCircle,
  Cross,
  Plus,
  Return,
  Save,
} from "common-v2/components/icons"
import { Alert } from "common-v2/components/alert"
import Table, { actionColumn, Cell } from "common-v2/components/table"
import Dialog, { Confirm } from "common-v2/components/dialog"
import Autocomplete from "common-v2/components/autocomplete"
import TagAutocomplete from "common-v2/components/tag-autocomplete"
import { RadioGroup } from "common-v2/components/radio"
import { useRights } from "carbure/hooks/entity"
import { Panel } from "common-v2/components/scaffold"
import { formatDate } from "common-v2/utils/formatters"
import { compact } from "common-v2/utils/collection"
import {
  normalizeBiofuel,
  normalizeCountry,
  normalizeFeedstock,
} from "common-v2/utils/normalizers"
import { usePortal } from "common-v2/components/portal"
import { useMutation, useQuery } from "common-v2/hooks/async"
import * as api from "../api/production-sites"
import { useNotify } from "common-v2/components/notifications"

type ProductionSitesSettingsProps = {
  readOnly?: boolean
  entity: Entity
  getProductionSites?: typeof api.getProductionSites
}

const ProductionSitesSettings = ({
  readOnly,
  entity,
  getProductionSites = api.getProductionSites,
}: ProductionSitesSettingsProps) => {
  const { t } = useTranslation()
  const rights = useRights()
  const portal = usePortal()
  const notify = useNotify()

  const productionSites = useQuery(getProductionSites, {
    key: "production-sites",
    params: [entity.id],
  })

  const deleteProductionSite = useMutation(api.deleteProductionSite, {
    invalidates: ["production-sites"],

    onSuccess: () => {
      notify(t("Le site de production a bien été supprimé !"), {
        variant: "success",
      })
    },

    onError: () => {
      notify(t("Impossible de supprimer le site de production"), {
        variant: "danger",
      })
    },
  })

  const canModify = !readOnly && rights.is(UserRole.Admin, UserRole.ReadWrite)
  const prodSitesData = productionSites.result?.data.data ?? []

  function showProductionSite(prodSite: ProductionSiteDetails) {
    portal((close) => (
      <ProductionSiteDialog
        readOnly
        title={t("Détails du site de production")}
        entity={entity}
        productionSite={prodSite}
        onClose={close}
      />
    ))
  }

  function createProductionSite() {
    portal((close) => (
      <ProductionSiteDialog
        entity={entity}
        title={t("Ajout site de production")}
        description={t("Veuillez entrer les informations de votre nouveau site de production.")} // prettier-ignore
        onClose={close}
      />
    ))
  }

  function editProductionSite(prodSite: ProductionSiteDetails) {
    portal((close) => (
      <ProductionSiteDialog
        title={t("Modification site de production")}
        description={t("Veuillez entrer les nouvelles informations de votre site de production.")} // prettier-ignore
        entity={entity}
        productionSite={prodSite}
        readOnly={!canModify}
        onClose={close}
      />
    ))
  }

  function removeProductionSite(prodSite: ProductionSiteDetails) {
    portal((close) => (
      <Confirm
        title={t("Suppression site")}
        description={t("Voulez-vous vraiment supprimer le site de production {{site}} ?", { site: prodSite.name })} // prettier-ignore
        confirm={t("Supprimer")}
        icon={Cross}
        variant="danger"
        onClose={close}
        onConfirm={() => deleteProductionSite.execute(entity.id, prodSite.id)}
      />
    ))
  }

  return (
    <Panel id="production">
      <header>
        <h1>{t("Sites de production")}</h1>
        {canModify && (
          <Button
            asideX
            variant="primary"
            icon={Plus}
            action={createProductionSite}
            label={t("Ajouter un site de production")}
          />
        )}
      </header>

      {prodSitesData.length === 0 && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun site de production trouvé</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

      {prodSitesData.length > 0 && (
        <Table
          rows={prodSitesData}
          onAction={readOnly ? showProductionSite : editProductionSite}
          columns={[
            {
              header: t("ID"),
              cell: (ps) => <Cell text={`${ps.site_id}`} />,
            },
            {
              header: t("Nom"),
              cell: (ps) => <Cell text={ps.name} />,
            },
            {
              header: t("Pays"),
              cell: (ps) => (
                <Cell text={t(ps.country?.code_pays, { ns: "countries" })} />
              ),
            },
            {
              header: t("Date de mise en service"),
              cell: (ps) => <Cell text={formatDate(ps.date_mise_en_service)} />,
            },
            actionColumn<ProductionSiteDetails>((prodSite) =>
              compact([
                canModify && (
                  <Button
                    captive
                    variant="icon"
                    icon={Cross}
                    title={t("Supprimer le site de production")}
                    action={() => removeProductionSite(prodSite)}
                  />
                ),
              ])
            ),
          ]}
        />
      )}

      {productionSites.loading && <LoaderOverlay />}
    </Panel>
  )
}

type ProductionSiteDialogProps = {
  title: string
  description?: string
  entity: Entity
  productionSite?: ProductionSiteDetails
  readOnly?: boolean
  onClose: () => void
}

interface ProductionSiteForm {
  site_id: string | undefined
  name: string | undefined
  date_mise_en_service: string | undefined
  ges_option: GESOption | undefined
  eligible_dc: boolean
  dc_reference: string | undefined
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

export const ProductionSiteDialog = ({
  title,
  entity,
  description,
  productionSite,
  readOnly,
  onClose,
}: ProductionSiteDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const addProdSite = useMutation(addProductionSite, {
    invalidates: ["production-sites"],

    onSuccess: () => {
      notify(t("Le site de production a bien été créé !"), {
        variant: "success",
      })
      onClose()
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

  const { value, bind } = useForm<ProductionSiteForm>({
    site_id: productionSite?.site_id ?? "",
    name: productionSite?.name ?? "",
    date_mise_en_service: productionSite?.date_mise_en_service ?? "",
    ges_option: productionSite?.ges_option ?? GESOption.Default,

    eligible_dc: productionSite?.eligible_dc ?? false,
    dc_reference: productionSite?.dc_reference ?? "",

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

  const canSave = Boolean(
    value.country && value.date_mise_en_service && value.name
  )

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
    <Dialog onClose={onClose}>
      <header>
        <h1>{title}</h1>
      </header>

      <main>
        {description && (
          <section>
            <p>{description}</p>
          </section>
        )}

        <section>
          <Form id="production-site" onSubmit={submitProductionSite}>
            <TextInput
              readOnly={readOnly}
              label={t("Nom du site")}
              {...bind("name")}
            />

            <Row style={{ gap: "var(--spacing-s)" }}>
              <TextInput
                readOnly={readOnly}
                label={t("N° d'identification (SIRET)")}
                {...bind("site_id")}
              />
              <TextInput
                readOnly={readOnly}
                type="date"
                label={t("Date de mise en service")}
                {...bind("date_mise_en_service")}
              />
            </Row>

            <hr />

            <Row style={{ gap: "var(--spacing-s)" }}>
              <TextInput
                readOnly={readOnly}
                label={t("Ville")}
                {...bind("city")}
              />
              <TextInput
                readOnly={readOnly}
                label={t("Code postal")}
                {...bind("postal_code")}
              />
            </Row>

            <Autocomplete
              readOnly={readOnly}
              label={t("Pays")}
              placeholder={t("Rechercher un pays...")}
              getOptions={common.findCountries}
              normalize={normalizeCountry}
              {...bind("country")}
            />

            <hr />

            <TextInput
              readOnly={readOnly}
              label={t("Nom du gérant")}
              {...bind("manager_name")}
            />

            <Row style={{ gap: "var(--spacing-s)" }}>
              <TextInput
                readOnly={readOnly}
                label={t("N° de téléphone du gérant")}
                {...bind("manager_phone")}
              />
              <TextInput
                readOnly={readOnly}
                label={t("Addresse email du gérant")}
                {...bind("manager_email")}
              />
            </Row>

            <hr />

            <Checkbox
              disabled
              label={t("Éligible double-comptage ?")}
              {...bind("eligible_dc")}
            />
            {value.eligible_dc && (
              <TextInput
                disabled
                label={t("Référence double-comptage")}
                {...bind("dc_reference")}
              />
            )}

            <hr />

            <RadioGroup
              disabled={readOnly}
              label={t("Options GES")}
              options={gesOptions}
              {...bind("ges_option")}
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
            />
            <TagAutocomplete
              readOnly={readOnly}
              label={t("Biocarburants")}
              placeholder={t("Ajouter biocarburants...")}
              defaultOptions={value.biocarburants}
              getOptions={common.findBiofuels}
              normalize={normalizeBiofuel}
              {...bind("biocarburants")}
            />

            <hr />

            <TagAutocomplete
              readOnly={readOnly}
              label={t("Certificats (2BS, ISCC)")}
              placeholder={t("Rechercher des certificats...")}
              defaultOptions={value.certificates}
              getOptions={(search) => common.findMyCertificates(search, { entity_id: entity.id })} // prettier-ignore
              {...bind("certificates")}
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
            disabled={!canSave}
            label={t("Sauvegarder")}
          />
        )}
        <Button asideX={readOnly} icon={Return} action={() => onClose()}>
          <Trans>Retour</Trans>
        </Button>
      </footer>
    </Dialog>
  )
}

async function addProductionSite(entity: Entity, form: ProductionSiteForm) {
  const res = await api.addProductionSite(
    entity.id,
    form.name!,
    form.date_mise_en_service!,
    form.country!.code_pays,
    form.ges_option!,
    form.site_id!,
    form.city!,
    form.postal_code!,
    form.eligible_dc,
    form.dc_reference!,
    form.manager_name!,
    form.manager_phone!,
    form.manager_email!
  )

  const psite = res.data.data!

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
  form: ProductionSiteForm
) {
  await api.updateProductionSite(
    entity.id,
    psite.id,
    form.name!,
    form.date_mise_en_service!,
    form.country!.code_pays,
    form.ges_option!,
    form.site_id!,
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

export default ProductionSitesSettings
