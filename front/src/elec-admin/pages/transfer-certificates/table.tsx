import Table, { Cell, Order } from "common/components/table"
import { formatDate } from "common/utils/formatters"
import { ElecTransferCertificatePreview } from "elec/types"

import { memo } from "react"
import { useTranslation } from "react-i18next"
import TransferCertificateTag from "../../../elec/components/transfer-certificates/tag"
import TransferCertificateTiruertTag from "../../../elec/components/transfer-certificates/tiruert-tag"
import { To } from "react-router-dom"

export interface ElecAdminTransferCertificateTableProps {
  loading: boolean
  transferCertificates: ElecTransferCertificatePreview[]
  order: Order | undefined
  rowLink: (row: ElecTransferCertificatePreview) => To
  onOrder: (order: Order | undefined) => void
  selected: number[]
  onSelect: (selected: number[]) => void
  tiruert?: boolean
}

export const ElecAdminTransferCertificateTable = memo(
  ({
    loading,
    transferCertificates,
    order,
    onOrder,
    rowLink,
    tiruert = false,
  }: ElecAdminTransferCertificateTableProps) => {
    const columns = useColumns(tiruert || false)
    const displayedColumns = [
      columns.status,
      ...(tiruert ? [columns.consumption_date] : []),
      columns.cpo,
      columns.transfer_date,
      columns.operator,
      columns.energy_amount,
      columns.certificate_id,
    ]
    return (
      <Table
        loading={loading}
        order={order}
        onOrder={onOrder}
        rowLink={rowLink}
        rows={transferCertificates}
        columns={displayedColumns}
      />
    )
  }
)

export function useColumns(tiruert: boolean) {
  const { t } = useTranslation()
  const tiruertStatusLabel = t("Statut TIRUERT")
  const statusLabel = t("Statut")
  return {
    status: {
      key: "status",
      header: t(tiruert ? tiruertStatusLabel : statusLabel),
      cell: (transferCertificate: ElecTransferCertificatePreview) => {
        if (tiruert) {
          return (
            <TransferCertificateTiruertTag
              used_in_tiruert={transferCertificate.used_in_tiruert}
            />
          )
        } else {
          return <TransferCertificateTag status={transferCertificate.status} />
        }
      },
    },

    consumption_date: {
      key: "consumption_date",
      header: t("Date de déclaration"),
      cell: (transferCertificate: ElecTransferCertificatePreview) => {
        const value = formatDate(
          transferCertificate.consumption_date,
          "MM/yyyy"
        )
        return <Cell text={value} />
      },
    },
    cpo: {
      key: "cpo",
      header: t("Aménageur"),
      cell: (transferCertificate: ElecTransferCertificatePreview) => {
        const value = transferCertificate.supplier.name
        return <Cell text={value} />
      },
    },
    operator: {
      key: "operator",
      header: t("Redevable"),
      cell: (transferCertificate: ElecTransferCertificatePreview) => {
        const value = transferCertificate.client.name
        return <Cell text={value} />
      },
    },

    transfer_date: {
      key: "transfer_date",
      header: t("Date d'émission"),
      cell: (transferCertificate: ElecTransferCertificatePreview) => {
        const value = formatDate(transferCertificate.transfer_date)
        return <Cell text={value} />
      },
    },
    energy_amount: {
      key: "energy_amount",
      header: t("MWh"),
      cell: (transferCertificate: ElecTransferCertificatePreview) => {
        return <Cell text={transferCertificate.energy_amount} />
      },
    },
    certificate_id: {
      key: "certificate_id",
      header: t("Numéro"),
      cell: (transferCertificate: ElecTransferCertificatePreview) => {
        return <Cell text={transferCertificate.certificate_id} />
      },
    },
  }
}

export default ElecAdminTransferCertificateTable
