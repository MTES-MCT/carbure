import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import {
  UserRightRequest,
  UserRightStatus,
  UserRole,
  EntityPreview,
} from "common/types"
import { useUser } from "common/hooks/user"

import * as api from "../api"
import * as common from "common/api"
import { useMutation } from "common/hooks/async"
import { usePortal } from "common/components/portal"
import { formatDate } from "common/utils/formatters"
import {
  getEntityTypeLabel,
  getUserRoleLabel,
  normalizeEntityPreview,
} from "common/utils/normalizers"
import { Button } from "common/components/button"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import { Alert } from "common/components/alert"
import { AlertTriangle, Cross, Plus, Return } from "common/components/icons"
import Table, { actionColumn, Cell } from "common/components/table"
import Dialog, { Confirm } from "common/components/dialog"
import Autocomplete from "common/components/autocomplete"
import { RadioGroup } from "common/components/radio"
import Tag, { TagVariant } from "common/components/tag"
import Form from "common/components/form"
import { useMatomo } from "matomo"
import { useNotify } from "common/components/notifications"
import { useNavigate } from "react-router-dom"

export const AccountAccesRights = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  const navigate = useNavigate()

  const user = useUser()

  const revokeMyself = useMutation(api.revokeMyself, {
    invalidates: ["user-settings"],
  })

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
        <>
          <section>
            <Alert variant="warning" icon={AlertTriangle}>
              <Trans>
                Aucune autorisation pour ce compte, ajoutez une organisation
                pour continuer.
              </Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

      {user.requests.length > 0 && (
        <Table
          onAction={(right) =>
            right.status === UserRightStatus.Accepted &&
            navigate(`/org/${right.entity.id}`)
          }
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
              cell: (r) => (
                <Cell text={getEntityTypeLabel(r.entity.entity_type)} />
              ),
            },
            {
              header: t("Droits"),
              cell: (r) => <Cell text={getUserRoleLabel(r.role)} />,
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
                captive
                variant="icon"
                icon={Cross}
                title={t("Annuler")}
                action={() =>
                  portal((close) => (
                    <Confirm
                      icon={Cross}
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

export interface EntityDialogProps {
  onClose: () => void
}

export const EntityDialog = ({ onClose }: EntityDialogProps) => {
  const { t } = useTranslation()
  const matomo = useMatomo()
  const notify = useNotify()
  const navigate = useNavigate()

  const [entity, setEntity] = useState<EntityPreview | undefined>(undefined)
  const [role, setRole] = useState<UserRole | undefined>(UserRole.ReadOnly)

  const requestAccess = useMutation(api.requestAccess, {
    invalidates: ["user-settings"],
    onSuccess: () =>
      notify(t("La société a été ajoutée !"), { variant: "success" }),
    onError: () =>
      notify(t("La société n'a pas pu être ajoutée !"), { variant: "danger" }),
  })

  const showAddCompanyDialog = () => {
    onClose()
    navigate("/account/company-registration")
  }

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
          <Form
            id="access-right"
            onSubmit={async () => {
              matomo.push(["trackEvent", "account", "add-access-right"])
              await requestAccess.execute(entity!.id, role!)
              setEntity(undefined)
            }}
          >
            <Autocomplete
              autoFocus
              label={t("Organisation")}
              placeholder={t("Rechercher une société...")}
              name="entity"
              value={entity}
              getOptions={common.findEnabledEntities}
              onChange={setEntity}
              normalize={normalizeEntityPreview}
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
          <Button
            variant="link"
            label={t("Ma société n'est pas enregistrée sur CarbuRe.")}
            action={showAddCompanyDialog}
          />
        </section>
      </main>
      <footer>
        <Button
          variant="primary"
          loading={requestAccess.loading}
          icon={Plus}
          label={t("Demander l'accès")}
          disabled={!entity || !role}
          submit="access-right"
        />
        <Button asideX icon={Return} action={onClose} label={t("Retour")} />
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
