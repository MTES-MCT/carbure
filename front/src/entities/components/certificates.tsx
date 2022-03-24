import { useTranslation } from "react-i18next"
import { EntityCertificate } from "common/types"
import { LoaderOverlay, Panel } from "common-v2/components/scaffold"
import Table, { actionColumn, Cell } from "common-v2/components/table"
import Button from "common-v2/components/button"
import { Check, Return } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import Dialog from "common-v2/components/dialog"
import { useMutation, useQuery } from "common-v2/hooks/async"
import * as api from "../api-v2"
import { useNotify } from "common-v2/components/notifications"
import NoResult from "transactions/components/no-result"
import { compact, matchesSearch } from "common-v2/utils/collection"

type CertificatesProps = {
  search?: string
  entity?: number
}

const Certificates = ({ search = "", entity }: CertificatesProps) => {
  const { t } = useTranslation()

  const certificates = useQuery(api.getEntityCertificates, {
    key: "entity-certificates",
    params: [entity],
  })

  const certData = (certificates.result?.data?.data ?? []).filter((c) =>
    matchesSearch(search, [
      c.certificate.certificate_id,
      c.certificate.certificate_holder,
      c.certificate.certificate_type,
      c.entity.name,
      c.entity.entity_type,
    ])
  )

  return (
    <Panel id="certificates">
      <header>
        <h1>{t("Certificats")}</h1>
      </header>
      {certData.length === 0 && (
        <section style={{ paddingBottom: "var(--spacing-l)" }}>
          <NoResult />
        </section>
      )}
      {certData.length > 0 && (
        <Table
          rows={certData}
          columns={compact([
            entity === undefined && {
              key: "entities",
              header: "Société",
              orderBy: (e) => e.entity.name,
              cell: (e) => (
                <Cell text={e.entity.name} sub={t(e.entity.entity_type)} />
              ),
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
              key: "validity",
              header: t("Validité"),
              orderBy: (c) => c.certificate.valid_until,
              cell: (c) => <Cell text={c.certificate.valid_until} />,
            },
            actionColumn<EntityCertificate>((c) =>
              compact([
                !c.checked_by_admin && <CheckCertificate certificate={c} />,
              ])
            ),
          ])}
        />
      )}

      {certificates.loading && <LoaderOverlay />}
    </Panel>
  )
}

interface ActionProps {
  certificate: EntityCertificate
}

const CheckCertificate = ({ certificate }: ActionProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const notify = useNotify()

  const checkCertificate = useMutation(api.checkEntityCertificate, {
    invalidates: ["entity-certificates"],
    onSuccess() {
      notify(t("Le certificat a été validé !"), { variant: "success" })
    },
    onError() {
      notify(t("Le certificat n'a pas pu être validé !"), { variant: "danger" })
    },
  })

  return (
    <Button
      variant="icon"
      title={t("Valider le certificat")}
      icon={Check}
      action={() =>
        portal((close) => (
          <Dialog onClose={close}>
            <header>
              <h1>{t("Valider le certificat")}</h1>
            </header>
            <main>
              <p>{t("Voulez-vous valider ce certificat ?")}</p>
            </main>
            <footer>
              <Button
                asideX
                loading={checkCertificate.loading}
                variant="primary"
                icon={Check}
                label={t("Valider")}
                action={() =>
                  checkCertificate.execute(certificate.id).then(close)
                }
              />
              <Button icon={Return} label={t("Annuler")} action={close} />
            </footer>
          </Dialog>
        ))
      }
    />
  )
}

export default Certificates
