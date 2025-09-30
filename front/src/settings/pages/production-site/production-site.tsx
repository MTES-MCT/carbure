import { Trans, useTranslation } from "react-i18next"

import { Entity, ProductionSiteDetails, UserRole } from "common/types"

import { useRights } from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Confirm } from "common/components/dialog2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { Table, Cell } from "common/components/table2"
import { useMutation, useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import * as api from "../../api/production-sites"
import { ProductionSiteDialog } from "./production-site-dialog"
import { Notice } from "common/components/notice"
import { EditableCard } from "common/molecules/editable-card"

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
  const notifyError = useNotifyError()

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

    onError: (e) => {
      notifyError(e)
    },
  })

  const canModify = !readOnly && rights.is(UserRole.Admin, UserRole.ReadWrite)
  const prodSitesData = productionSites.result?.data?.results ?? []

  function showProductionSite(prodSite: ProductionSiteDetails) {
    portal((close) => (
      <ProductionSiteDialog
        readOnly
        title={t("Détails du site de production")}
        productionSite={prodSite}
        onClose={close}
      />
    ))
  }

  function createProductionSite() {
    portal((close) => (
      <ProductionSiteDialog
        title={t("Ajout site de production")}
        description={t("Veuillez entrer les informations de votre nouveau site de production.")} // prettier-ignore
        onClose={close}
      />
    ))
  }

  function editProductionSite(prodSite: ProductionSiteDetails) {
    portal((close) => (
      <ProductionSiteDialog
        title={t("Détails du site de production")}
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
        icon="ri-close-line"
        customVariant="danger"
        onClose={close}
        onConfirm={() => deleteProductionSite.execute(entity.id, prodSite.id)}
        hideCancel
      />
    ))
  }

  return (
    <EditableCard
      title={t("Sites de production")}
      description={t("Gérez les sites de production de votre entreprise ici.")}
      headerActions={
        canModify && (
          <Button asideX iconId="ri-add-line" onClick={createProductionSite}>
            {t("Ajouter un site de production")}
          </Button>
        )
      }
    >
      {prodSitesData.length === 0 && (
        <Notice icon="ri-error-warning-line" variant="warning">
          <Trans>Aucun site de production trouvé</Trans>
        </Notice>
      )}

      {prodSitesData.length > 0 && (
        <Table
          rows={prodSitesData}
          onAction={readOnly ? showProductionSite : editProductionSite}
          columns={[
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
              cell: (ps) =>
                ps.date_mise_en_service && (
                  <Cell text={formatDate(ps.date_mise_en_service)} />
                ),
            },
            {
              header: t("Action"),
              cell: (ps) =>
                canModify && (
                  <Button
                    captive
                    priority="tertiary no outline"
                    iconId="ri-close-line"
                    title={t("Supprimer le site de production")}
                    onClick={() => removeProductionSite(ps)}
                    style={{ color: "var(--text-default-grey)" }}
                  />
                ),
            },
          ]}
        />
      )}

      {productionSites.loading && <LoaderOverlay />}
    </EditableCard>
  )
}

export default ProductionSitesSettings
