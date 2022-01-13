import { useState } from "react"
import {
  Entity,
  EntityType,
  UserRightRequest,
  UserRightStatus,
  UserRole,
} from "common/types"
import colStyles from "common/components/table.module.css"
import pendingStyles from "carbure/components/pending.module.css"
import { LoaderOverlay, Title } from "common/components"
import { Button } from "common/components/button"
import { AlertTriangle, Cross, Plus } from "common-v2/components/icons"
import { formatDate, SettingsForm } from "settings/components/common"
import { LabelAutoComplete } from "common/components/autocomplete"
import { Alert } from "common/components/alert"
import Table, {
  Actions,
  Column,
  Line,
  Row,
  padding,
} from "common/components/table"
import { Section, SectionBody, SectionHeader } from "common/components/section"
import {
  confirm,
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  prompt,
  PromptProps,
} from "common/components/dialog"
import { Label } from "common/components/input"
import RadioGroup from "common/components/radio-group"
import * as api from "../api"
import * as common from "common/api"
import useAPI from "common/hooks/use-api"
import { Trans, useTranslation } from "react-i18next"
import { reloadUserSettings, useUserContext } from "carbure/hooks/user"
import Badge, { Variant } from "common/components/badge"

export const AccountAccesRights = () => {
  const { t } = useTranslation()

  const user = useUserContext()

  const [revoking, revokeMyself] = useAPI(api.revokeMyself)
  const [requesting, resolveAccess] = useAPI(api.requestAccess)

  async function askEntityAccess() {
    const res = await prompt<AccessRequest>((resolve) => (
      <EntityPrompt onResolve={resolve} />
    ))

    if (res) {
      const { entity, role } = res
      await resolveAccess(entity.id, "", role)
      reloadUserSettings()
    }
  }

  const loading = user.loading || requesting.loading || revoking.loading

  const entityTypes = {
    [EntityType.Administration]: t("Administration"),
    [EntityType.Operator]: t("Opérateur"),
    [EntityType.Producer]: t("Producteur"),
    [EntityType.Auditor]: t("Auditeur"),
    [EntityType.Trader]: t("Trader"),
    [EntityType.ExternalAdmin]: t("Administration Externe"),
  }

  const roleLabels = {
    [UserRole.ReadOnly]: t("Lecture seule"),
    [UserRole.ReadWrite]: t("Lecture/écriture"),
    [UserRole.Admin]: t("Administration"),
    [UserRole.Auditor]: t("Audit"),
  }

  const columns: Column<UserRightRequest>[] = [
    padding,
    statusColumn,
    {
      header: t("Organisation"),
      render: (r) => <Line text={r.entity.name} />,
    },
    {
      header: t("Type"),
      render: (r) => <Line text={entityTypes[r.entity.entity_type]} />,
    },
    {
      header: t("Droits"),
      render: (r) => <Line text={roleLabels[r.role]} />,
    },
    {
      header: t("Date"),
      render: (r) => {
        const dateRequested = formatDate(r.date_requested)
        const dateExpired = r.expiration_date ? formatDate(r.expiration_date) : null // prettier-ignore

        return dateExpired
          ? t(`{{dateRequested}} (expire le {{dateExpired}})`, { dateRequested, dateExpired }) // prettier-ignore
          : dateRequested
      },
    },
    padding,
  ]

  const actions = Actions<UserRightRequest>([
    {
      title: t("Annuler"),
      icon: Cross,
      action: async (r) => {
        const shouldRevoke = await confirm(
          t("Annuler mes accès"),
          t(`Voulez vous annuler votre accès à {{entity}} ?`, { entity: r.entity.name }) // prettier-ignore
        )

        if (shouldRevoke) {
          await revokeMyself(r.entity.id)
          reloadUserSettings()
        }
      },
    },
  ])

  const rows: Row<UserRightRequest>[] = user.requests.map((r) => ({ value: r }))

  return (
    <Section>
      <SectionHeader>
        <Title>
          <Trans>Demandes d'accès aux sociétés</Trans>
        </Title>
        <Button level="primary" icon={Plus} onClick={askEntityAccess}>
          <Trans>Ajouter une organisation</Trans>
        </Button>
      </SectionHeader>

      {user.requests.length === 0 && (
        <SectionBody>
          <Alert level="warning" icon={AlertTriangle}>
            <Trans>
              Aucune autorisation pour ce compte, ajoutez une organisation pour
              continuer.
            </Trans>
          </Alert>
        </SectionBody>
      )}

      {user.requests.length > 0 && (
        <Table columns={[...columns, actions]} rows={rows} />
      )}

      {loading && <LoaderOverlay />}
    </Section>
  )
}

export type AccessRequest = {
  entity: Entity
  role: UserRole
}

export const EntityPrompt = ({ onResolve }: PromptProps<AccessRequest>) => {
  const { t } = useTranslation()

  const [entity, setEntity] = useState<Entity | null>(null)
  const [role, setRole] = useState<UserRole>(UserRole.ReadOnly)

  const roleDetails = {
    [UserRole.ReadOnly]: t("Lecture seule (consultation des lots uniquement)"),
    [UserRole.ReadWrite]: t("Lecture/écriture (création et gestion des lots)"),
    [UserRole.Admin]: t("Administration (contrôle complet de la société sur CarbuRe)"), // prettier-ignore
    [UserRole.Auditor]: t("Audit (accès spécial pour auditeurs)"),
  }

  return (
    <Dialog onResolve={onResolve}>
      <SettingsForm>
        <DialogTitle text={t("Ajout organisation")} />
        <DialogText
          text={t("Recherchez la société qui vous emploie pour pouvoir accéder à ses données.")} // prettier-ignore
        />
        <LabelAutoComplete
          label={t("Organisation")}
          placeholder={t("Rechercher une société...")}
          name="entity"
          value={entity}
          getQuery={common.findEntities}
          onChange={(e: any) => setEntity(e.target.value)}
          getValue={(e) => `${e.id}`}
          getLabel={(e) => e.name}
        />
        <Label label={t("Rôle")}>
          <RadioGroup
            name="role"
            options={Object.entries(roleDetails).map(([v, l]) => ({
              value: v,
              label: l,
            }))}
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
          />
        </Label>
        <a
          href="mailto:carbure@beta.gouv.fr"
          target="_blank"
          rel="noreferrer"
          className={pendingStyles.link}
        >
          <Trans>Ma société n'est pas enregistrée sur CarbuRe.</Trans>
        </a>
        <DialogButtons>
          <Button
            level="primary"
            icon={Plus}
            disabled={!entity}
            onClick={() => entity && onResolve({ entity, role })}
          >
            <Trans>Demander l'accès</Trans>
          </Button>
          <Button onClick={() => onResolve()}>
            <Trans>Annuler</Trans>
          </Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

export const RightStatus = ({ status }: { status: UserRightStatus }) => {
  const { t } = useTranslation()

  const statusLabels = {
    [UserRightStatus.Pending]: t("En attente"),
    [UserRightStatus.Accepted]: t("Accepté"),
    [UserRightStatus.Rejected]: t("Refusé"),
    [UserRightStatus.Revoked]: t("Révoqué"),
  }

  const statusVariant: Record<UserRightStatus, Variant> = {
    [UserRightStatus.Accepted]: "success",
    [UserRightStatus.Pending]: "info",
    [UserRightStatus.Rejected]: "danger",
    [UserRightStatus.Revoked]: "warning",
  }

  return <Badge variant={statusVariant[status]}>{statusLabels[status]}</Badge>
}

export const statusColumn = {
  header: "Statut",
  className: colStyles.narrowColumn,
  render: (r: UserRightRequest) => <RightStatus status={r.status} />,
}
