import React, { useState } from "react"
import cl from "clsx"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api-v2"
import css from "./settings.module.css"
import useEntity from "carbure/hooks/entity"
import { useNotify } from "common-v2/components/notifications"
import { useQuery, useMutation } from "common-v2/hooks/async"
import { usePortal } from "common-v2/components/portal"
import { formatDate } from "common-v2/utils/formatters"
import { Panel } from "common-v2/components/scaffold"
import Button from "common-v2/components/button"
import Dialog, { Confirm } from "common-v2/components/dialog"
import Table, { Cell, actionColumn } from "common-v2/components/table"
import Autocomplete from "common-v2/components/autocomplete"
import {
  Cross,
  Plus,
  Return,
  Refresh,
  AlertCircle,
} from "common-v2/components/icons"
import {
  normalizeCertificate,
  normalizeEntityCertificate,
} from "common-v2/utils/normalizers"
import { Certificate, EntityCertificate } from "common/types"
import { isExpired } from "./common"
import Alert from "common-v2/components/alert"
import Select from "common-v2/components/select"

const Certificates = () => {
  const { t } = useTranslation()
  const entity = useEntity()
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

  const certificateData = certificates.result?.data.data ?? []

  return (
    <Panel style={{ marginBottom: "var(--spacing-l)" }}>
      <header>
        <h1>{t("Certificats")}</h1>
        <Button
          asideX
          variant="primary"
          icon={Plus}
          label={t("Ajouter un certificat")}
          action={() =>
            portal((close) => <CertificateAddDialog onClose={close} />)
          }
          style={{ fontSize: "0.87em" }}
        />
      </header>

      <section>
        <Select
          label={t("Certificat par défaut")}
          placeholder={t("Sélectionner un certificat")}
          value={entity.default_certificate}
          onChange={setDefaultCertificate.execute}
          options={certificateData}
          normalize={normalizeEntityCertificate}
          style={{ flex: 1 }}
        />
      </section>

      {certificateData.length === 0 && (
        <section style={{ paddingBottom: "var(--spacing-l)" }}>
          <Alert
            variant="warning"
            icon={AlertCircle}
            label={t("Aucun certificat associé à cette société")}
          />
        </section>
      )}

      {certificateData.length > 0 && (
        <Table
          rows={certificateData}
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
              key: "validity",
              header: t("Validité"),
              orderBy: (c) => c.certificate.valid_until,
              cell: (c) => <ExpirationDate link={c} />,
            },
            actionColumn<EntityCertificate>((c) => [
              <Button
                variant="icon"
                icon={Cross}
                action={() =>
                  portal((close) => (
                    <Confirm
                      title={t("Suppression certificat")}
                      description={t("Voulez-vous supprimer ce certificat ?")}
                      confirm={t("Supprimer")}
                      variant="danger"
                      onConfirm={() =>
                        deleteCertificate.execute(
                          entity.id,
                          c.certificate.certificate_id,
                          c.certificate.certificate_type
                        )
                      }
                      onClose={close}
                    />
                  ))
                }
              />,
            ]),
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
    onSuccess: () =>
      notify(t("Le certificat a bien été ajouté !"), { variant: "success" }),
    onError: () =>
      notify(t("Le certificat n'a pas pu être ajouté !"), {
        variant: "danger",
      }),
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
          <Autocomplete
            label={t("Rechercher un certificat")}
            value={certificate}
            onChange={setCertificate}
            getOptions={(query) =>
              api.getCertificates(query).then((res) => res.data.data ?? [])
            }
            normalize={normalizeCertificate}
          />
        </section>
      </main>
      <footer>
        <Button asideX icon={Return} label={t("Retour")} action={onClose} />
        <Button
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
      </footer>
    </Dialog>
  )
}

type ExpirationDateProps = {
  link: EntityCertificate
}

export const ExpirationDate = ({ link }: ExpirationDateProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const expired = isExpired(link.certificate.valid_until)
  const formatted = formatDate(link.certificate.valid_until)
  const updated = link.has_been_updated

  return (
    <span className={cl(css.expirationDate, expired && css.expired)}>
      {expired && !updated && (
        <React.Fragment>
          {formatted}
          <Button
            captive
            icon={Refresh}
            label={t("Mise à jour")}
            action={() =>
              portal((close) => (
                <CertificateUpdateDialog
                  oldCertificate={link.certificate}
                  onClose={close}
                />
              ))
            }
          />
        </React.Fragment>
      )}

      {expired && updated && <Trans>Mis à jour ({{ formatted }})</Trans>}

      {!expired && formatted}
    </span>
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
      onClose()
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
          <Autocomplete
            label={t("Rechercher un certificat")}
            value={certificate}
            onChange={setCertificate}
            getOptions={(query) =>
              api.getCertificates(query).then((res) => res.data.data ?? [])
            }
            normalize={normalizeCertificate}
          />
        </section>
      </main>
      <footer>
        <Button asideX icon={Return} label={t("Retour")} action={onClose} />
        <Button
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
      </footer>
    </Dialog>
  )
}

export default Certificates
