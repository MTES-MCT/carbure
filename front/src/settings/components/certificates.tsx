import React, { useState, Fragment } from "react"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api/certificates"
import useEntity, { useRights } from "carbure/hooks/entity"
import { useNotify } from "common/components/notifications"
import { useQuery, useMutation } from "common/hooks/async"
import { usePortal } from "common/components/portal"
import { formatDate } from "common/utils/formatters"
import { Panel, Row } from "common/components/scaffold"
import Button from "common/components/button"
import Dialog, { Confirm } from "common/components/dialog"
import Table, { Cell, actionColumn } from "common/components/table"
import Autocomplete from "common/components/autocomplete"
import {
  Cross,
  Plus,
  Return,
  Refresh,
  AlertCircle,
} from "common/components/icons"
import {
  normalizeCertificate,
  normalizeEntityCertificate,
} from "carbure/utils/normalizers"
import { Certificate, EntityCertificate, UserRole } from "carbure/types"
import Alert from "common/components/alert"
import Select from "common/components/select"
import isBefore from "date-fns/isBefore"
import { compact } from "common/utils/collection"
import Form from "common/components/form"

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
    <Panel id="certificates">
      <header>
        <h1>{t("Certificats")}</h1>
        {canModify && (
          <Button
            asideX
            variant="primary"
            icon={Plus}
            label={t("Ajouter un certificat")}
            action={() =>
              portal((close) => <CertificateAddDialog onClose={close} />)
            }
          />
        )}
      </header>

      <section>
        <Select
          disabled={!canModify}
          label={t("Certificat par défaut")}
          placeholder={t("Sélectionner un certificat")}
          value={entity.default_certificate ?? undefined}
          onChange={setDefaultCertificate.execute}
          options={validCertificates}
          normalize={normalizeEntityCertificate}
          style={{ flex: 1 }}
        />
      </section>

      {certificateData.length === 0 && (
        <>
          <section>
            <Alert
              variant="warning"
              icon={AlertCircle}
              label={t("Aucun certificat associé à cette société")}
            />
          </section>
          <footer />
        </>
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
              key: "validition",
              header: t("Validation"),
              orderBy: (c) => c?.rejected_by_admin?.toString() ?? "",
              cell: (c) => <Validation link={c} />,
            },
            actionColumn<EntityCertificate>((c) =>
              compact([
                canModify && (
                  <Button
                    captive
                    variant="icon"
                    icon={Cross}
                    action={() =>
                      portal((close) => (
                        <Confirm
                          title={t("Suppression certificat")}
                          description={t(
                            "Voulez-vous supprimer ce certificat ?"
                          )}
                          confirm={t("Supprimer")}
                          icon={Cross}
                          variant="danger"
                          onClose={close}
                          onConfirm={() =>
                            deleteCertificate.execute(
                              entity.id,
                              c.certificate.certificate_id,
                              c.certificate.certificate_type
                            )
                          }
                        />
                      ))
                    }
                  />
                ),
              ])
            ),
          ]}
        />
      )}
    </Panel>
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
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Ajouter un certificat")}</h1>
      </header>
      <main>
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
      </main>
      <footer>
        <Button
          asideX
          submit="add-certificate"
          loading={addCertificate.loading}
          disabled={!certificate}
          variant="primary"
          icon={Plus}
          label={t("Ajouter")}
          action={() =>
            addCertificate.execute(
              entity.id,
              certificate!.certificate_id,
              certificate!.certificate_type
            )
          }
        />
        <Button icon={Return} label={t("Retour")} action={onClose} />
      </footer>
    </Dialog>
  )
}

type ValidationProps = {
  link: EntityCertificate
}

export const Validation = ({ link }: ValidationProps) => {
  const { t } = useTranslation()

  const expired = isExpired(link.certificate.valid_until)

  const getValidationString = (): string => {
    if (expired) return t("Expiré")
    if (link.rejected_by_admin) return t("Refusé")
    if (link.checked_by_admin) return t("Accepté")
    return t("En cours")
  }

  const getRowStyle = (): { color: string } | undefined => {
    if (link.rejected_by_admin || expired)
      return { color: "var(--orange-dark)" }
    if (!link.checked_by_admin) return { color: "var(--orange-medium)" }
    return undefined
  }

  return <Row style={getRowStyle()}>{getValidationString()}</Row>
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
              icon={Refresh}
              label={t("Mettre à jour")}
              action={() =>
                portal((close) => (
                  <CertificateUpdateDialog
                    oldCertificate={link.certificate}
                    onClose={close}
                  />
                ))
              }
            />
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
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Mettre à jour un certificat")}</h1>
      </header>
      <main>
        <section>
          {t(
            "Vous pouvez rechercher parmi les certificats recensés sur Carbure et ajouter celui qui remplacera le certificat expiré."
          )}
        </section>
        <section>
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
          <Alert variant="info" style={{ display: "inline-block" }}>
            <strong>{t("Votre certificat n'est pas dans la liste ?")}</strong>
            <p>
              {t(
                "La liste des certificats approuvés par CarbuRe est mise à jour automatiquement tous les dimanches en se référant à la liste publique des certificats affichés sur les sites internet des organismes certificateurs."
              )}
            </p>
          </Alert>
        </section>
      </main>
      <footer>
        <Button
          asideX
          submit="replace-certificate"
          loading={updateCertificate.loading}
          disabled={!certificate}
          variant="primary"
          icon={Refresh}
          label={t("Mettre à jour")}
          action={() =>
            updateCertificate.execute(
              entity.id,
              oldCertificate!.certificate_id,
              oldCertificate!.certificate_type,
              certificate!.certificate_id,
              certificate!.certificate_type
            )
          }
        />
        <Button icon={Return} label={t("Retour")} action={onClose} />
      </footer>
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
