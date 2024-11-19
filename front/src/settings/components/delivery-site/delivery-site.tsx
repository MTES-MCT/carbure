import { Trans, useTranslation } from "react-i18next"
import {
  Entity,
  EntityType,
  UserRole,
  Depot,
  EntityDepot,
  OwnershipType,
} from "carbure/types"
import * as common from "carbure/api"
import * as api from "../../api/delivery-sites"
import { LoaderOverlay } from "common/components/scaffold"
import Checkbox from "common/components/checkbox"
import Button from "common/components/button"
import { AlertCircle, Cross, Plus } from "common/components/icons"
import { Alert } from "common/components/alert"
import Table, { actionColumn, Cell } from "common/components/table"
import { Confirm, Dialog } from "common/components/dialog"
import AutoComplete from "common/components/autocomplete"
import { RadioGroup } from "common/components/radio"
import { Form, useForm } from "common/components/form"
import useEntity, { useRights } from "carbure/hooks/entity"
import { Panel } from "common/components/scaffold"
import { normalizeDepot } from "carbure/utils/normalizers"
import { compact } from "common/utils/collection"
import { useMutation, useQuery } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { CreateDeliverySiteDialog } from "./create-delivery-site-dialog"
import { DeliverySiteDialog } from "./delivery-site-dialog"
import {
  useDepotTypeLabels,
  useOwnerShipTypeOptions,
} from "./delivery-site.hooks"
import { AutoCompleteOperators } from "carbure/components/autocomplete-operators"

interface DeliverySiteSettingsProps {
  readOnly?: boolean
  entity: Entity
  getDepots?: typeof api.getDeliverySites
}

const DeliverySitesSettings = ({
  readOnly,
  entity,
  getDepots = api.getDeliverySites,
}: DeliverySiteSettingsProps) => {
  const { t } = useTranslation()
  const rights = useRights()
  const portal = usePortal()
  const depotTypeLabels = useDepotTypeLabels()

  const deliverySites = useQuery(getDepots, {
    key: "delivery-sites",
    params: [entity.id],
  })

  const deliverySitesData = deliverySites.result?.data.data ?? []
  const isEmpty = deliverySitesData.length === 0

  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  function findDeliverySite() {
    portal((close) => <DeliverySiteFinderDialog onClose={close} />)
  }

  function showDeliverySite(deliverySite: EntityDepot) {
    portal((close) => (
      <DeliverySiteDialog deliverySite={deliverySite} onClose={close} />
    ))
  }

  return (
    <Panel id="depot">
      <header>
        <h1>
          <Trans>Dépôts</Trans>
        </h1>
        {!readOnly && canModify && (
          <Button
            asideX
            variant="primary"
            icon={Plus}
            label={t("Ajouter un dépôt")}
            action={findDeliverySite}
          />
        )}
      </header>

      {isEmpty && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun dépôt trouvé</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

      {!isEmpty && (
        <Table
          rows={deliverySitesData}
          onAction={showDeliverySite}
          columns={[
            {
              key: "id",
              header: t("ID"),
              orderBy: (ds) => ds.depot?.depot_id ?? "",
              cell: (ds) => <Cell text={ds.depot!.depot_id} />,
            },
            {
              key: "name",
              header: t("Nom"),
              orderBy: (ds) => ds.depot?.name ?? "",
              cell: (ds) => <Cell text={ds.depot!.name} />,
            },
            {
              key: "type",
              header: t("Type"),
              cell: (ds) => (
                <Cell
                  text={
                    ds.depot?.site_type
                      ? depotTypeLabels[ds.depot?.site_type]
                      : ""
                  }
                />
              ),
            },
            {
              key: "city",
              header: t("Ville"),
              orderBy: (ds) => ds.depot?.city ?? "",
              cell: (ds) => (
                <Cell
                  text={`${ds.depot!.city}, ${t(ds.depot!.country.code_pays, {
                    ns: "countries",
                  })}`}
                />
              ),
            },
            actionColumn<EntityDepot>((ds) =>
              compact([
                !readOnly && canModify && (
                  <DeleteDeliverySiteButton deliverySite={ds} />
                ),
              ])
            ),
          ]}
        />
      )}

      {deliverySites.loading && <LoaderOverlay />}
    </Panel>
  )
}

type DeliverySiteFinderDialogProps = {
  onClose: () => void
}

export const DeliverySiteFinderDialog = ({
  onClose,
}: DeliverySiteFinderDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const portal = usePortal()
  const ownerShipTypeOptions = useOwnerShipTypeOptions()

  const addDeliverySite = useMutation(api.addDeliverySite, {
    invalidates: ["delivery-sites"],

    onSuccess: () => {
      notify(t("Le dépôt a bien été ajouté !"), { variant: "success" })
      onClose()
    },

    onError: () => {
      notify(t("Impossible d'ajouter le dépôt."), { variant: "danger" })
    },
  })

  const { value, bind } = useForm({
    depot: undefined as Depot | undefined,
    ownership_type: OwnershipType.ThirdParty as OwnershipType | undefined,
    blending_is_outsourced: false,
    blender: undefined as Entity | undefined,
  })

  async function submitDepot() {
    if (!value.depot) return

    await addDeliverySite.execute(
      entity.id,
      value.depot.depot_id,
      value.ownership_type!,
      value.blending_is_outsourced,
      value.blender
    )
  }

  const openCreateDeliverySiteDialog = () => {
    portal((close) => <CreateDeliverySiteDialog onClose={close} />)
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Ajouter un dépôt")}</h1>
      </header>

      <main>
        <section>
          <p>{t("Veuillez rechercher un dépôt que vous utilisez.")}</p>
        </section>

        <section>
          <Form id="add-depot" onSubmit={submitDepot}>
            <AutoComplete
              autoFocus
              label={t("Dépôt à ajouter")}
              placeholder={t("Rechercher un dépôt...")}
              getOptions={(search) => common.findDepots(search)}
              normalize={normalizeDepot}
              required
              {...bind("depot")}
            />

            <RadioGroup
              label={t("Propriété")}
              options={ownerShipTypeOptions}
              {...bind("ownership_type")}
            />

            {entity && entity.entity_type === EntityType.Operator && (
              <Checkbox
                label={t("Incorporation potentiellement effectuée par un tiers")} // prettier-ignore
                {...bind("blending_is_outsourced")}
              />
            )}
            {value.blending_is_outsourced && (
              <AutoCompleteOperators
                label={t("Incorporateur Tiers")}
                placeholder={t("Rechercher un opérateur pétrolier...")}
                {...bind("blender")}
              />
            )}

            <Button variant="link" action={openCreateDeliverySiteDialog}>
              <Trans>
                Le dépôt que je recherche n'est pas enregistré sur CarbuRe.
              </Trans>
            </Button>
          </Form>
        </section>
      </main>

      <footer>
        <Button
          asideX
          loading={addDeliverySite.loading}
          variant="primary"
          submit="add-depot"
          icon={Plus}
          label={t("Ajouter")}
        />
        <Button action={onClose} label={t("Annuler")} />
      </footer>
    </Dialog>
  )
}

const DeleteDeliverySiteButton = ({
  deliverySite,
}: {
  deliverySite: EntityDepot
}) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const portal = usePortal()

  const entity = useEntity()

  const deleteDeliverySite = useMutation(api.deleteDeliverySite, {
    invalidates: ["delivery-sites"],

    onSuccess: () => {
      notify(t("Le dépôt a bien été supprimé !"), { variant: "success" })
    },

    onError: () => {
      notify(t("Impossible de supprimer le dépôt."), { variant: "danger" })
    },
  })

  return (
    <Button
      captive
      variant="icon"
      icon={Cross}
      title={t("Supprimer le dépôt")}
      action={() =>
        portal((close) => (
          <Confirm
            title={t("Supprimer dépôt")}
            description={t("Voulez-vous supprimer le dépôt {{depot}} de votre liste ?", { depot: deliverySite.depot!.name })} // prettier-ignore
            confirm={t("Supprimer")}
            icon={Cross}
            variant="danger"
            onClose={close}
            onConfirm={async () => {
              if (deliverySite.depot) {
                await deleteDeliverySite.execute(
                  entity.id,
                  deliverySite.depot.depot_id
                )
              }
            }}
          />
        ))
      }
    />
  )
}

export default DeliverySitesSettings
