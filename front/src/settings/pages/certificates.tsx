import { useState, Fragment } from "react"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api/certificates"
import useEntity, { useRights } from "common/hooks/entity"
import { useNotify } from "common/components/notifications"
import { useQuery, useMutation } from "common/hooks/async"
import { usePortal } from "common/components/portal"
import { formatDate } from "common/utils/formatters"
import { Row } from "common/components/scaffold"
import { Button } from "common/components/button2"
import { Dialog, Confirm } from "common/components/dialog2"
import { Cell, Table } from "common/components/table2"
import { Autocomplete } from "common/components/autocomplete2"
import {
  normalizeCertificate,
  normalizeEntityCertificate,
} from "common/utils/normalizers"
import { Certificate, EntityCertificate, UserRole } from "common/types"
import { isBefore } from "date-fns"
import { Form } from "common/components/form2"
import { EditableCard } from "common/molecules/editable-card"
import Badge, { BadgeProps } from "@codegouvfr/react-dsfr/Badge"
import i18next from "i18next"
import { Notice } from "common/components/notice"

const Certificates = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const rights = useRights()
  const notify = useNotify()
  const portal = usePortal()

  const certificates = useQuery(api.getMyCertificates, {
    key: "my-certificates",
    params: [entity.id],
  })

  const deleteCertificate = useMutation(api.deleteCertificate, {
    invalidates: ["my-certificates"],
    onSuccess: () => {
      notify(t("Le certificat a bien été supprimé !"), { variant: "success" })
    },
    onError: () => {
      notify(t("Le certificat n'a pas pu être supprimé !"), {
        variant: "danger",
      })
    },
  })

  const setDefaultCertificate = useMutation(
    (cert: string | undefined) => api.setDefaultCertificate(entity.id, cert!),
    { invalidates: ["user-settings"] }
  )

  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)
  const certificateData = certificates.result?.data ?? []
  const validCertificates = certificateData.filter(e => !isExpired(e.certificate.valid_until)) // prettier-ignore

  return (
    <EditableCard
      title={t("Certificats")}
      headerActions={
        canModify ? (
          <Button
            asideX
            iconId="ri-add-line"
            onClick={() =>
              portal((close) => <CertificateAddDialog onClose={close} />)
            }
          >
            {t("Ajouter un certificat")}
          </Button>
        ) : null
      }
    >
      <Autocomplete
        disabled={!canModify}
        label={t("Certificat par défaut")}
        placeholder={t("Sélectionner un certificat")}
        value={entity.default_certificate ?? undefined}
        onChange={setDefaultCertificate.execute}
        options={validCertificates}
        normalize={normalizeEntityCertificate}
        style={{ flex: 1 }}
      />

      {certificateData.length === 0 && (
        <Notice
          variant="warning"
          icon="ri-error-warning-line"
          title={t("Aucun certificat associé à cette société")}
        />
      )}

      {certificateData.length > 0 && (
        <Table
          rows={certificateData}
          rowProps={(cert) => ({
            style: cert.has_been_updated ? { opacity: 0.5 } : undefined,
          })}
          onAction={(c) => {
            if (c.certificate.download_link) {
              window.open(c.certificate.download_link)
            }
          }}
          columns={[
            {
              key: "validition",
              header: t("Statut"),
              orderBy: (c) => getValidationString({ link: c }),
              cell: (c) => <Validation link={c} />,
            },

            {
              key: "id",
              header: t("ID"),
              orderBy: (c) => c.certificate.certificate_id,
              cell: (c) => <Cell text={c.certificate.certificate_id} />,
            },
            {
              key: "type",
              header: t("Type"),
              orderBy: (c) => c.certificate.certificate_type,
              cell: (c) => <Cell text={c.certificate.certificate_type} />,
            },
            {
              key: "holder",
              header: t("Détenteur"),
              orderBy: (c) => c.certificate.certificate_holder,
              cell: (c) => <Cell text={c.certificate.certificate_holder} />,
            },
            {
              key: "scope",
              header: t("Périmètre"),
              orderBy: (c) =>
                c.certificate.scope ? String(c.certificate.scope) : "-",
              cell: (c) => (
                <Cell
                  text={c.certificate.scope ? String(c.certificate.scope) : "-"}
                />
              ),
            },
            {
              key: "expiration",
              header: t("Expiration"),
              orderBy: (c) => c.certificate.valid_until,
              cell: (c) => <ExpirationDate link={c} readOnly={!canModify} />,
            },
            {
              header: t("Action"),
              cell: (c) =>
                canModify && (
                  <Button
                    captive
                    iconId="ri-close-line"
                    title="Delete certificate"
                    priority="tertiary no outline"
                    style={{ color: "var(--text-default-grey)" }}
                    onClick={() =>
                      portal((close) => (
                        <Confirm
                          title={t("Suppression certificat")}
                          description={t(
                            "Voulez-vous supprimer ce certificat ?"
                          )}
                          confirm={t("Supprimer")}
                          icon="ri-close-line"
                          customVariant="danger"
                          onClose={close}
                          onConfirm={() =>
                            deleteCertificate.execute(
                              entity.id,
                              c.certificate.certificate_id,
                              c.certificate.certificate_type
                            )
                          }
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
    </EditableCard>
  )
}

interface CertificateAddDialogProps {
  onClose: () => void
}

const CertificateAddDialog = ({ onClose }: CertificateAddDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()

  const [certificate, setCertificate] = useState<Certificate | undefined>(
    undefined
  )

  const addCertificate = useMutation(api.addCertificate, {
    invalidates: ["my-certificates"],
    onSuccess: () => {
      notify(t("Le certificat a bien été ajouté !"), { variant: "success" })
      onClose()
    },
    onError: () => {
      notify(t("Le certificat n'a pas pu être ajouté !"), {
        variant: "danger",
      })
    },
  })

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Ajouter un certificat")}</Dialog.Title>}
      footer={
        <Button
          asideX
          type="submit"
          nativeButtonProps={{
            form: "add-certificate",
          }}
          loading={addCertificate.loading}
          disabled={!certificate}
          iconId="ri-add-line"
          onClick={() =>
            addCertificate.execute(
              entity.id,
              certificate!.certificate_id,
              certificate!.certificate_type
            )
          }
        >
          {t("Ajouter")}
        </Button>
      }
    >
      <section>
        {t(
          "Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui vous correspond."
        )}
      </section>
      <section>
        <Form id="add-certificate">
          <Autocomplete
            autoFocus
            label={t("Rechercher un certificat")}
            value={certificate}
            onChange={setCertificate}
            getOptions={(query) =>
              api.getCertificates(query).then((res) => res.data ?? [])
            }
            normalize={normalizeCertificate}
          />
        </Form>
      </section>
    </Dialog>
  )
}

type ValidationProps = {
  link: EntityCertificate
}

const getValidationString = ({ link }: ValidationProps): string => {
  const expired = isExpired(link.certificate.valid_until)

  if (expired) return i18next.t("Expiré")
  if (link.rejected_by_admin) return i18next.t("Refusé")
  if (link.checked_by_admin) return i18next.t("Accepté")
  return i18next.t("En cours")
}

export const Validation = ({ link }: ValidationProps) => {
  const expired = isExpired(link.certificate.valid_until)

  const getSeverity = (): BadgeProps["severity"] => {
    if (expired) return "warning"
    if (link.rejected_by_admin) return "error"
    if (link.checked_by_admin) return "success"
    return "info"
  }

  return <Badge severity={getSeverity()}>{getValidationString({ link })}</Badge>
}

type ExpirationDateProps = {
  link: EntityCertificate
  readOnly?: boolean
}

export const ExpirationDate = ({ link, readOnly }: ExpirationDateProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const expired = isExpired(link.certificate.valid_until)
  const formatted = formatDate(link.certificate.valid_until)
  const updated = link.has_been_updated

  return (
    <Row
      style={
        expired
          ? {
              alignItems: "center",
              color: "var(--orange-dark)",
              gap: "var(--spacing-s)",
            }
          : undefined
      }
    >
      {expired && !updated && (
        <Fragment>
          {!readOnly ? (
            <Button
              captive
              priority="tertiary"
              iconId="ri-arrow-go-forward-line"
              onClick={() =>
                portal((close) => (
                  <CertificateUpdateDialog
                    oldCertificate={link.certificate}
                    onClose={close}
                  />
                ))
              }
            >
              {t("Mettre à jour")}
            </Button>
          ) : (
            formatted
          )}
        </Fragment>
      )}

      {expired && updated && <Trans>Mis à jour ({{ formatted }})</Trans>}

      {!expired && formatted}
    </Row>
  )
}

interface CertificateUpdateDialogProps {
  oldCertificate: Certificate
  onClose: () => void
}

const CertificateUpdateDialog = ({
  oldCertificate,
  onClose,
}: CertificateUpdateDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()

  const [certificate, setCertificate] = useState<Certificate | undefined>(
    undefined
  )

  const updateCertificate = useMutation(api.updateCertificate, {
    invalidates: ["my-certificates"],
    onSuccess: () => {
      notify(t("Le certificat a bien été mis à jour !"), { variant: "success" })
      onClose()
    },
    onError: () => {
      notify(t("Le certificat n'a pas pu être mis à jour !"), {
        variant: "danger",
      })
    },
  })

  return (
    <Dialog
      size="medium"
      onClose={onClose}
      header={<Dialog.Title>{t("Mettre à jour un certificat")}</Dialog.Title>}
      footer={
        <Button
          asideX
          type="submit"
          nativeButtonProps={{
            form: "replace-certificate",
          }}
          loading={updateCertificate.loading}
          disabled={!certificate}
          iconId="ri-arrow-go-forward-line"
          onClick={() =>
            updateCertificate.execute(
              entity.id,
              oldCertificate!.certificate_id,
              oldCertificate!.certificate_type,
              certificate!.certificate_id,
              certificate!.certificate_type
            )
          }
        >
          {t("Mettre à jour")}
        </Button>
      }
    >
      <p>
        {t(
          "Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui remplacera le certificat expiré."
        )}
      </p>

      <Form id="replace-certificate">
        <Autocomplete
          autoFocus
          label={t("Rechercher un certificat")}
          value={certificate}
          onChange={setCertificate}
          getOptions={(query) =>
            api.getCertificates(query).then((res) => res.data ?? [])
          }
          normalize={normalizeCertificate}
        />
      </Form>
      <Notice
        variant="info"
        title={t("Votre certificat n'est pas dans la liste ?")}
      >
        <p>
          {t(
            "La liste des certificats approuvés par CarbuRe est mise à jour automatiquement tous les dimanches en se référant à la liste publique des certificats affichés sur les sites internet des organismes certificateurs."
          )}
        </p>
      </Notice>
    </Dialog>
  )
}

export function isExpired(date: string) {
  try {
    const now = new Date()
    const valid_until = new Date(date)
    return isBefore(valid_until, now)
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (e) {
    return false
  }
}

export default Certificates
