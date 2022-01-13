import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import {
  Entity,
  EntityType,
  UserRightRequest,
  UserRightStatus,
  UserRole,
} from "carbure/types"
import { useUser } from "carbure/hooks/user"

import * as api from "../api"
import * as common from "common-v2/api"
import { useMutation } from "common-v2/hooks/async"
import { usePortal } from "common-v2/components/portal"
import { formatDate } from "common-v2/utils/formatters"
import { normalizeEntity } from "common-v2/utils/normalizers"
import { Button, ExternalLink } from "common-v2/components/button"
import { LoaderOverlay, Panel } from "common-v2/components/scaffold"
import { Alert } from "common-v2/components/alert"
import { AlertTriangle, Cross, Plus, Return } from "common-v2/components/icons"
import Table, { actionColumn, Cell } from "common-v2/components/table"
import Dialog, { Confirm } from "common-v2/components/dialog"
import Autocomplete from "common-v2/components/autocomplete"
import { RadioGroup } from "common-v2/components/radio"
import Tag, { TagVariant } from "common-v2/components/tag"
import Form from "common-v2/components/form"

export const AccountAccesRights = () => {
  const { t } = useTranslation()
  const portal = usePortal()

  const user = useUser()

  const revokeMyself = useMutation(api.revokeMyself, {
    invalidates: ["user-settings"],
  })

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

  const loading = user.loading || revokeMyself.loading

  return (
    <Panel>
      <header>
        <h1>
          <Trans>Demandes d'accès aux sociétés</Trans>
        </h1>
        <Button
          asideX
          variant="primary"
          icon={Plus}
          label={t("Ajouter une organisation")}
          action={() => portal((close) => <EntityDialog onClose={close} />)}
        />
      </header>

      {user.requests.length === 0 && (
        <section style={{ paddingBottom: "var(--spacing-l)" }}>
          <Alert variant="warning" icon={AlertTriangle}>
            <Trans>
              Aucune autorisation pour ce compte, ajoutez une organisation pour
              continuer.
            </Trans>
          </Alert>
        </section>
      )}

      {user.requests.length > 0 && (
        <Table
          rows={user.requests}
          columns={[
            {
              small: true,
              header: "Statut",
              cell: (r: UserRightRequest) => <RightStatus status={r.status} />,
            },
            {
              header: t("Organisation"),
              cell: (r) => <Cell text={r.entity.name} />,
            },
            {
              header: t("Type"),
              cell: (r) => <Cell text={entityTypes[r.entity.entity_type]} />,
            },
            {
              header: t("Droits"),
              cell: (r) => <Cell text={roleLabels[r.role]} />,
            },
            {
              header: t("Date"),
              cell: (r) => {
                const dateRequested = formatDate(r.date_requested)
                const dateExpired = r.expiration_date ? formatDate(r.expiration_date) : null // prettier-ignore
                return dateExpired
                  ? t(`{{dateRequested}} (expire le {{dateExpired}})`, { dateRequested, dateExpired }) // prettier-ignore
                  : dateRequested
              },
            },
            actionColumn<UserRightRequest>((right) => [
              <Button
                variant="icon"
                icon={Cross}
                title={t("Annuler")}
                action={() =>
                  portal((close) => (
                    <Confirm
                      variant="danger"
                      title={t("Annuler mes accès")}
                      description={t(`Voulez vous annuler votre accès à {{entity}} ?`, { entity: right.entity.name })} // prettier-ignore
                      confirm={t("Révoquer")}
                      onConfirm={() => revokeMyself.execute(right.entity.id)}
                      onClose={close}
                    />
                  ))
                }
              />,
            ]),
          ]}
        />
      )}

      {loading && <LoaderOverlay />}
    </Panel>
  )
}

export type AccessRequest = {
  entity: Entity
  role: UserRole
}

export interface EntityDialogProps {
  onClose: () => void
}

export const EntityDialog = ({ onClose }: EntityDialogProps) => {
  const { t } = useTranslation()

  const [entity, setEntity] = useState<Entity | undefined>(undefined)
  const [role, setRole] = useState<UserRole | undefined>(UserRole.ReadOnly)

  const requestAccess = useMutation(api.requestAccess, {
    invalidates: ["user-settings"],
  })

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Ajout organisation")}</h1>
      </header>
      <main>
        <section>
          {t(
            "Recherchez la société qui vous emploie pour pouvoir accéder à ses données."
          )}
        </section>
        <section>
          <Form>
            <Autocomplete
              label={t("Organisation")}
              placeholder={t("Rechercher une société...")}
              name="entity"
              value={entity}
              getOptions={common.findEntities}
              onChange={setEntity}
              normalize={normalizeEntity}
            />

            <RadioGroup
              label={t("Rôle")}
              name="role"
              value={role}
              onChange={setRole}
              options={[
                {
                  value: UserRole.ReadOnly,
                  label: t("Lecture seule (consultation des lots uniquement)"),
                },
                {
                  value: UserRole.ReadWrite,
                  label: t("Lecture/écriture (création et gestion des lots)"),
                },
                {
                  value: UserRole.Admin,
                  label: t("Administration (contrôle complet de la société sur CarbuRe)"), // prettier-ignore
                },
                {
                  value: UserRole.Auditor,
                  label: t("Audit (accès spécial pour auditeurs)"),
                },
              ]}
            />
          </Form>
        </section>
        <section>
          <ExternalLink href="mailto:carbure@beta.gouv.fr">
            <Trans>Ma société n'est pas enregistrée sur CarbuRe.</Trans>
          </ExternalLink>
        </section>
      </main>
      <footer>
        <Button
          variant="primary"
          loading={requestAccess.loading}
          icon={Plus}
          label={t("Demander l'accès")}
          disabled={!entity || !role}
          action={() => requestAccess.execute(entity!.id, role!)}
        />
        <Button icon={Return} action={onClose} label={t("Retour")} />
      </footer>
    </Dialog>
  )
}

export const RightStatus = ({ status }: { status: UserRightStatus }) => {
  const { t } = useTranslation()

  const statusVariant: Record<UserRightStatus, TagVariant> = {
    [UserRightStatus.Accepted]: "success",
    [UserRightStatus.Pending]: "info",
    [UserRightStatus.Rejected]: "danger",
    [UserRightStatus.Revoked]: "warning",
  }

  const statusLabels = {
    [UserRightStatus.Pending]: t("En attente"),
    [UserRightStatus.Accepted]: t("Accepté"),
    [UserRightStatus.Rejected]: t("Refusé"),
    [UserRightStatus.Revoked]: t("Révoqué"),
  }

  return <Tag variant={statusVariant[status]} label={statusLabels[status]} />
}
