import { Trans, useTranslation } from "react-i18next"

import { Country, DepotType, OwnershipType } from "common/types"
import { EntityType, UserRole } from "carbure/types"
import {
  DeliverySiteSettingsHook,
  EntityDeliverySite,
} from "../hooks/use-delivery-sites"

import styles from "./settings.module.css"

import * as common from "common/api"

import { Box, LoaderOverlay } from "common/components"
import { LabelInput, Label, LabelCheckbox } from "common/components/input"
import Button, { MailTo } from "common-v2/components/button"
import { AlertCircle, Cross, Plus, Return } from "common-v2/components/icons"
import { Alert } from "common/components/alert"
import Table, {
  Actions,
  arrow,
  Column,
  Line,
  Row,
  padding,
} from "common/components/table"
import {
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"
import { LabelAutoComplete } from "common/components/autocomplete"
import RadioGroup from "common/components/radio-group"
import { SettingsForm } from "./common"
import useForm from "common/hooks/use-form"
import { Entity } from "carbure/types"
import { useRights } from "carbure/hooks/entity"
import { Panel } from "common-v2/components/scaffold"

type DeliverySiteFinderPromptProps = PromptProps<EntityDeliverySite> & {
  entity: Entity
}

export const DeliverySiteFinderPrompt = ({
  entity,
  onResolve,
}: DeliverySiteFinderPromptProps) => {
  const { t } = useTranslation()

  const { data, hasChange, onChange } = useForm<EntityDeliverySite>({
    depot: null,
    ownership_type: OwnershipType.ThirdParty,
    blending_is_outsourced: false,
    blender: null,
  })

  const ownerShipTypes = [
    { value: OwnershipType.Own, label: "Propre" },
    { value: OwnershipType.ThirdParty, label: "Tiers" },
    { value: OwnershipType.Processing, label: "Processing" },
  ]

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={t("Ajouter dépôt")} />
      <DialogText text={t("Veuillez rechercher un dépôt que vous utilisez.")} />

      <SettingsForm>
        <LabelAutoComplete
          label={t("Dépôt")}
          placeholder={t("Rechercher un dépôt...")}
          name="depot"
          value={data.depot}
          getQuery={common.findDeliverySites}
          onChange={onChange}
          getValue={(d) => d.depot_id}
          getLabel={(d) => d.name}
          queryArgs={[entity?.id]}
        />

        <Label label="Propriété">
          <RadioGroup
            row
            value={data.ownership_type}
            name="ownership_type"
            options={ownerShipTypes}
            onChange={onChange}
          />
        </Label>

        {entity && entity.entity_type === EntityType.Operator && (
          <LabelCheckbox
            name="blending_is_outsourced"
            label={t("Incorporation potentiellement effectuée par un tiers")}
            checked={data.blending_is_outsourced}
            onChange={onChange}
          />
        )}
        {data.blending_is_outsourced && (
          <LabelAutoComplete
            label={t("Incorporateur Tiers")}
            placeholder={t("Rechercher un opérateur pétrolier...")}
            name="blender"
            value={data.blender}
            getQuery={common.findOperators}
            onChange={onChange}
            getValue={(c) => c.id.toString()}
            getLabel={(c) => c.name}
          />
        )}

        <MailTo
          user="carbure"
          host="beta.gouv.fr"
          className={styles.settingsLink}
        >
          <Trans>
            Le dépôt que je recherche n'est pas enregistré sur CarbuRe.
          </Trans>
        </MailTo>

        <DialogButtons>
          <Button
            variant="primary"
            icon={Plus}
            disabled={!hasChange}
            action={() => onResolve(data)}
          >
            <Trans>Ajouter</Trans>
          </Button>
          <Button action={() => onResolve()}>
            <Trans>Annuler</Trans>
          </Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

type DeliverySiteState = {
  name: string
  city: string
  country: Country | null
  depot_id: string
  depot_type: DepotType
  address: string
  postal_code: string
  ownership_type: OwnershipType
  blending_is_outsourced: boolean
  blender: string
}

type DeliverySitePromptProps = PromptProps<EntityDeliverySite> & {
  title: string
  description?: string
  deliverySite?: EntityDeliverySite
}

export const DeliverySitePrompt = ({
  title,
  description,
  deliverySite,
  onResolve,
}: DeliverySitePromptProps) => {
  const { t } = useTranslation()

  const form: DeliverySiteState = {
    name: deliverySite?.depot?.name ?? "",
    city: deliverySite?.depot?.city ?? "",
    country: deliverySite?.depot?.country ?? null,
    depot_id: deliverySite?.depot?.depot_id ?? "",
    depot_type: deliverySite?.depot?.depot_type ?? DepotType.Other,
    address: deliverySite?.depot?.address ?? "",
    postal_code: deliverySite?.depot?.postal_code ?? "",
    ownership_type: deliverySite?.ownership_type ?? OwnershipType.Own,
    blending_is_outsourced: deliverySite?.blending_is_outsourced ?? false,
    blender: deliverySite?.blender?.name ?? "",
  }

  const depotTypes = [
    { value: DepotType.EFS, label: t("EFS") },
    { value: DepotType.EFPE, label: t("EFPE") },
    { value: DepotType.Other, label: t("Autre") },
    { value: DepotType.BiofuelDepot, label: t("Biofuel Depot") },
    { value: DepotType.OilDepot, label: t("Oil Depot") },
  ]

  const ownerShipTypes = [
    { value: OwnershipType.Own, label: t("Propre") },
    { value: OwnershipType.ThirdParty, label: t("Tiers") },
    { value: OwnershipType.Processing, label: t("Processing") },
  ]

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={title} />
      {description && <DialogText text={description} />}

      <SettingsForm>
        <hr />

        <Label label={t("Propriété")}>
          <RadioGroup
            row
            readOnly
            value={form.ownership_type}
            name="ownership_type"
            options={ownerShipTypes}
          />
        </Label>

        <hr />

        <Label label={t("Incorporation tierce")}>
          <LabelCheckbox
            disabled
            label={t("L'incorporation est effectuée par un tiers")}
            name="blending_is_outsourced"
            defaultChecked={form.blending_is_outsourced}
          />
          <LabelInput
            readOnly
            label={t("Incorporateur")}
            name="blender"
            value={form.blender}
          />
        </Label>
        <hr />

        <LabelInput
          readOnly
          label={t("Nom du site")}
          name="name"
          value={form.name}
        />
        <LabelInput
          readOnly
          label={t("ID de douane")}
          name="depot_id"
          value={form.depot_id}
        />

        <hr />

        <Label label={t("Type de dépôt")}>
          <RadioGroup
            row
            readOnly
            value={form.depot_type}
            name="depot_type"
            options={depotTypes}
          />
        </Label>

        <hr />

        <LabelInput
          readOnly
          label={t("Adresse")}
          name="address"
          value={form.address}
        />

        <Box row>
          <LabelInput
            readOnly
            label={t("Ville")}
            name="city"
            value={form.city}
          />
          <LabelInput
            readOnly
            label={t("Code postal")}
            name="postal_code"
            value={form.postal_code}
          />
        </Box>

        <LabelInput
          readOnly
          label={t("Pays")}
          placeholder={t("Rechercher un pays...")}
          name="country"
          value={
            form.country
              ? (t(form.country.code_pays, { ns: "countries" }) as string)
              : ""
          }
        />

        <hr />

        <DialogButtons>
          <Button icon={Return} action={() => onResolve()}>
            <Trans>Retour</Trans>
          </Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

type DeliverySitesSettingsProps = {
  settings: DeliverySiteSettingsHook
}

const DeliverySitesSettings = ({ settings }: DeliverySitesSettingsProps) => {
  const { t } = useTranslation()
  const rights = useRights()

  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  const depotTypeLabels = {
    [DepotType.EFS]: t("EFS"),
    [DepotType.EFPE]: t("EFPE"),
    [DepotType.Other]: t("Autre"),
    [DepotType.BiofuelDepot]: t("Biofuel Depot"),
    [DepotType.OilDepot]: t("Oil Depot"),
  }

  const actions =
    canModify && settings.deleteDeliverySite
      ? Actions([
          {
            icon: Cross,
            title: t("Supprimer le dépôt"),
            action: (ds: EntityDeliverySite) =>
              settings.deleteDeliverySite!(ds),
          },
        ])
      : arrow

  const columns: Column<EntityDeliverySite>[] = [
    padding,
    {
      header: t("ID"),
      render: (ds) => <Line text={ds.depot!.depot_id} />,
    },
    {
      header: t("Nom"),
      className: styles.settingsTableColumn,
      render: (ds) => <Line text={ds.depot!.name} />,
    },
    {
      header: t("Type"),
      render: (ds) => <Line text={depotTypeLabels[ds.depot!.depot_type]} />,
    },
    {
      header: t("Ville"),
      className: styles.settingsTableColumn,
      render: (ds) => (
        <Line
          text={`${ds.depot!.city}, ${t(ds.depot!.country.code_pays, {
            ns: "countries",
          })}`}
        />
      ),
    },
    actions,
  ]

  const rows: Row<EntityDeliverySite>[] = settings.deliverySites.map((ds) => ({
    value: ds,
    onClick: () => settings.showDeliverySite(ds),
  }))

  return (
    <Panel id="depot">
      <header>
        <h1>
          <Trans>Dépôts</Trans>
        </h1>
        {canModify && settings.addDeliverySite && (
          <Button
            asideX
            variant="primary"
            icon={Plus}
            action={settings.addDeliverySite}
          >
            <Trans>Ajouter un dépôt</Trans>
          </Button>
        )}
      </header>

      {settings.isEmpty && (
        <section style={{ marginBottom: "var(--spacing-l)" }}>
          <Alert icon={AlertCircle} level="warning">
            <Trans>Aucun dépôt trouvé</Trans>
          </Alert>
        </section>
      )}

      {!settings.isEmpty && (
        <Table columns={columns} rows={rows} className={styles.settingsTable} />
      )}

      {settings.isLoading && <LoaderOverlay />}
    </Panel>
  )
}

export default DeliverySitesSettings
