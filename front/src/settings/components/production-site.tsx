import { Trans, useTranslation } from "react-i18next"

import {
  Entity,
  ProductionSiteDetails,
  UserRole
} from "carbure/types"


import { useRights } from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { Confirm } from "common/components/dialog"
import { AlertCircle, Cross, Plus } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import Table, { Cell, actionColumn } from "common/components/table"
import { useMutation, useQuery } from "common/hooks/async"
import { compact } from "common/utils/collection"
import { formatDate } from "common/utils/formatters"
import * as api from "../api/production-sites"
import { ProductionSiteDialog } from "./production-site-dialog"

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

export default ProductionSitesSettings
