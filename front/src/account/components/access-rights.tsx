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
import { Button } from "common/components/button2"
import { LoaderOverlay } from "common/components/scaffold"
import { Table, Cell } from "common/components/table2"
import { Dialog, Confirm } from "common/components/dialog2"
import { Autocomplete } from "common/components/autocomplete2"
import { RadioGroup } from "common/components/inputs2"
import { Form } from "common/components/form2"
import { useMatomo } from "matomo"
import { useNotify } from "common/components/notifications"
import { Route, Routes, useNavigate } from "react-router-dom"
import Badge, { BadgeProps } from "@codegouvfr/react-dsfr/Badge"
import { EditableCard } from "common/molecules/editable-card"
import { Notice } from "common/components/notice"
import { ROUTE_URLS } from "common/utils/routes"
import { CompanyRegistrationDialog } from "companies/components/registration-dialog"
import { ForeignCompanyDialog } from "companies/components/foreign-company-dialog"

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
    <EditableCard
      title={t("Demandes d'accès aux sociétés")}
      headerActions={
        <Button
          asideX
          iconId="ri-add-line"
          linkProps={{
            to: ROUTE_URLS.MY_ACCOUNT.ADD_COMPANY,
          }}
        >
          {t("Ajouter une organisation")}
        </Button>
      }
    >
      {user.requests.length === 0 && (
        <Notice variant="warning" icon="ri-error-warning-line">
          <Trans>
            Aucune autorisation pour ce compte, ajoutez une organisation pour
            continuer.
          </Trans>
        </Notice>
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
              style: { minWidth: "160px" },
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
            {
              header: t("Actions"),
              cell: (right) => (
                <Button
                  captive
                  iconId="ri-close-line"
                  title={t("Annuler")}
                  priority="tertiary no outline"
                  onClick={() =>
                    portal((close) => (
                      <Confirm
                        icon="ri-close-line"
                        title={t("Annuler mes accès")}
                        description={t(`Voulez vous annuler votre accès à {{entity}} ?`, { entity: right.entity.name })} // prettier-ignore
                        confirm={t("Révoquer")}
                        onConfirm={() => revokeMyself.execute(right.entity.id)}
                        onClose={close}
                        hideCancel
                      />
                    ))
                  }
                />
              ),
            },
          ]}
        />
      )}

      {loading && <LoaderOverlay />}
      <Routes>
        <Route path="" element={null} />
        <Route
          path="add"
          element={
            <EntityDialog
              onClose={() => navigate(ROUTE_URLS.MY_ACCOUNT.COMPANIES)}
            />
          }
        />
        <Route path="registration" element={<CompanyRegistrationDialog />} />
        <Route
          path="registration/foreign"
          element={
            <ForeignCompanyDialog
              close={() => navigate(ROUTE_URLS.MY_ACCOUNT.COMPANIES)}
            />
          }
        />
      </Routes>
    </EditableCard>
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
    navigate(ROUTE_URLS.MY_ACCOUNT.COMPANY_REGISTRATION)
  }

  return (
    <Dialog
      onClose={onClose}
      header={
        <>
          <Dialog.Title>{t("Ajout organisation")}</Dialog.Title>
          <Dialog.Description>
            {t(
              "Recherchez la société qui vous emploie pour pouvoir accéder à ses données."
            )}
          </Dialog.Description>
        </>
      }
      footer={
        <Button
          loading={requestAccess.loading}
          iconId="ri-add-line"
          disabled={!entity || !role}
          type="submit"
          nativeButtonProps={{
            form: "access-right",
          }}
        >
          {t("Demander l'accès")}
        </Button>
      }
      fitContent
    >
      <Form
        id="access-right"
        onSubmit={async () => {
          matomo.push(["trackEvent", "account", "add-access-right"])
          await requestAccess.execute(entity!.id, role!)
          setEntity(undefined)
        }}
      >
        <div>
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
          <Button
            customPriority="link"
            onClick={showAddCompanyDialog}
            style={{ marginTop: "8px" }}
          >
            {t("Ma société n'est pas enregistrée sur CarbuRe.")}
          </Button>
        </div>

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
    </Dialog>
  )
}

export const RightStatus = ({ status }: { status: UserRightStatus }) => {
  const { t } = useTranslation()

  const statusVariant: Record<UserRightStatus, BadgeProps["severity"]> = {
    [UserRightStatus.Accepted]: "success",
    [UserRightStatus.Pending]: "info",
    [UserRightStatus.Rejected]: "error",
    [UserRightStatus.Revoked]: "warning",
  }

  const statusLabels = {
    [UserRightStatus.Pending]: t("En attente"),
    [UserRightStatus.Accepted]: t("Accepté"),
    [UserRightStatus.Rejected]: t("Refusé"),
    [UserRightStatus.Revoked]: t("Révoqué"),
  }

  return <Badge severity={statusVariant[status]}>{statusLabels[status]}</Badge>
}
