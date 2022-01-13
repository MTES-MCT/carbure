import { ApiState } from "common/hooks/use-api"
import { Certificate } from "common/types"
import { useTranslation } from "react-i18next"
import { Panel } from "common-v2/components/scaffold"
import Table, { Cell } from "common-v2/components/table"

type CertificatesProps = {
  certificates: ApiState<Certificate[]>
}

const Certificates = ({ certificates }: CertificatesProps) => {
  const { t } = useTranslation()
  return (
    <Panel style={{ marginBottom: "var(--spacing-l)" }}>
      <header>
        <h1>{t("Certificats")}</h1>
      </header>
      <Table
        rows={certificates.data ?? []}
        columns={[
          {
            key: "id",
            header: t("ID"),
            orderBy: (c) => c.certificate_id,
            cell: (c) => <Cell text={c.certificate_id} />,
          },
          {
            key: "type",
            header: t("Type"),
            orderBy: (c) => c.certificate_type,
            cell: (c) => <Cell text={c.certificate_type} />,
          },
          {
            key: "holder",
            header: t("Détenteur"),
            orderBy: (c) => c.certificate_holder,
            cell: (c) => <Cell text={c.certificate_holder} />,
          },
          {
            key: "validity",
            header: t("Validité"),
            orderBy: (c) => c.valid_until,
            cell: (c) => <Cell text={c.valid_until} />,
          },
        ]}
      />
    </Panel>
  )
}

export default Certificates
