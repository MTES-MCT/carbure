import { Trans, useTranslation } from "react-i18next"
import {
  Entity,
  EntityType,
  UserRole,
  Depot,
  EntityDepot,
  OwnershipType,
  EntityPreview,
  ExternalAdminPages,
} from "common/types"
import * as common from "common/api"
import * as api from "../../api/delivery-sites"
import { LoaderOverlay } from "common/components/scaffold"
import { Checkbox, RadioGroup } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { Cell, Column, Table } from "common/components/table2"
import { Confirm, Dialog } from "common/components/dialog2"
import { Autocomplete } from "common/components/autocomplete2"
import { Form, useForm } from "common/components/form2"
import useEntity, { hasAdminRight, useRights } from "common/hooks/entity"
import { normalizeDepot } from "common/utils/normalizers"
import { useMutation, useQuery } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { CreateDeliverySiteDialog } from "./create-delivery-site-dialog"
import { DeliverySiteDialog } from "./delivery-site-dialog"
import {
  useDepotTypeLabels,
  useOwnerShipTypeOptions,
} from "./delivery-site.hooks"
import { AutoCompleteOperators } from "common/molecules/autocomplete-operators"
import { EditableCard } from "common/molecules/editable-card"
import { Notice } from "common/components/notice"
import Badge from "@codegouvfr/react-dsfr/Badge"
import { compact } from "common/utils/collection"

interface DeliverySiteSettingsProps {
  readOnly?: boolean
  entity: Entity
  getDepots?: typeof common.getDeliverySites
}

const DeliverySitesSettings = ({
  readOnly,
  entity,
  getDepots = common.getDeliverySites,
}: DeliverySiteSettingsProps) => {
  const { t } = useTranslation()
  const rights = useRights()
  const portal = usePortal()
  const depotTypeLabels = useDepotTypeLabels()

  const deliverySites = useQuery(getDepots, {
    key: "delivery-sites",
    params: [entity.id],
  })

  const deliverySitesData = deliverySites.result?.data ?? []
  const isEmpty = deliverySitesData.length === 0

  const isDGDDI = hasAdminRight(ExternalAdminPages.DGDDI, entity)
  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite) && !isDGDDI

  function findDeliverySite() {
    portal((close) => <DeliverySiteFinderDialog onClose={close} />)
  }

  function showDeliverySite(deliverySite: EntityDepot) {
    portal((close) => (
      <DeliverySiteDialog deliverySite={deliverySite} onClose={close} />
    ))
  }

  return (
    <EditableCard
      title={t("Dépôts")}
      description={t("Gérez les dépôts de votre entreprise ici.")}
      headerActions={
        !readOnly &&
        canModify && (
          <Button asideX iconId="ri-add-line" onClick={findDeliverySite}>
            {t("Ajouter un dépôt")}
          </Button>
        )
      }
    >
      {isEmpty && (
        <Notice icon="ri-error-warning-line" variant="warning">
          <Trans>Aucun dépôt trouvé</Trans>
        </Notice>
      )}

      {!isEmpty && (
        <Table
          rows={deliverySitesData}
          onAction={showDeliverySite}
          columns={compact<Column<EntityDepot>>([
            !isDGDDI && {
              key: "status",
              header: t("Statut"),
              cell: (ds) => (
                <Badge severity={ds.depot?.is_enabled ? "success" : "info"}>
                  {ds.depot?.is_enabled ? t("Validé") : t("En attente")}
                </Badge>
              ),
            },
            {
              key: "id",
              header: t("ID"),
              orderBy: (ds) => ds.depot?.customs_id ?? "",
              cell: (ds) => <Cell text={ds.depot!.customs_id} />,
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
            !isDGDDI && {
              header: t("Action"),
              cell: (ds) =>
                !readOnly &&
                canModify && <DeleteDeliverySiteButton deliverySite={ds} />,
            },
          ])}
        />
      )}

      {deliverySites.loading && <LoaderOverlay />}
    </EditableCard>
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
    ownership_type: OwnershipType.THIRD_PARTY as OwnershipType | undefined,
    blending_is_outsourced: false,
    blender: undefined as EntityPreview | undefined,
  })

  async function submitDepot() {
    if (!value.depot || !value.depot.customs_id) return

    await addDeliverySite.execute(
      entity.id,
      value.depot.customs_id,
      value.ownership_type!,
      value.blending_is_outsourced,
      value.blender
    )
  }

  const openCreateDeliverySiteDialog = () => {
    portal((close) => <CreateDeliverySiteDialog onClose={close} />)
  }

  return (
    <Dialog
      onClose={onClose}
      header={
        <>
          <Dialog.Title>{t("Ajouter un dépôt")}</Dialog.Title>
          <Dialog.Description>
            {t("Veuillez rechercher un dépôt que vous utilisez.")}
          </Dialog.Description>
        </>
      }
      footer={
        <Button
          asideX
          loading={addDeliverySite.loading}
          type="submit"
          nativeButtonProps={{
            form: "add-depot",
          }}
          iconId="ri-add-line"
        >
          {t("Ajouter")}
        </Button>
      }
      fitContent
    >
      <Form
        id="add-depot"
        onSubmit={submitDepot}
        // Handle the box shadow of the button (the content of the dialog has overflow)
        style={{ paddingBottom: "2px" }}
      >
        <Autocomplete
          autoFocus
          label={t("Dépôt à ajouter")}
          placeholder={t("Rechercher un dépôt...")}
          getOptions={(search) => common.findDepots(search, false)}
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
        <Button customPriority="link" onClick={openCreateDeliverySiteDialog}>
          <Trans>
            Le dépôt que je recherche n'est pas enregistré sur CarbuRe.
          </Trans>
        </Button>
      </Form>
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
      priority="tertiary no outline"
      iconId="ri-close-line"
      title={t("Supprimer le dépôt")}
      onClick={() =>
        portal((close) => (
          <Confirm
            title={t("Supprimer dépôt")}
            description={t("Voulez-vous supprimer le dépôt {{depot}} de votre liste ?", { depot: deliverySite.depot!.name })} // prettier-ignore
            confirm={t("Supprimer")}
            icon="ri-close-line"
            customVariant="danger"
            onClose={close}
            onConfirm={async () => {
              if (deliverySite.depot?.customs_id) {
                await deleteDeliverySite.execute(
                  entity.id,
                  deliverySite.depot.customs_id
                )
              }
            }}
            hideCancel
          />
        ))
      }
      style={{ color: "var(--text-default-grey)" }}
    />
  )
}

export default DeliverySitesSettings
