import Table, { Cell, Order } from "common/components/table"
import { formatNumber } from "common/utils/formatters"
import { ElecProvisionCertificatePreview } from "elec/types"
import { getElecProvisionCertificateSourceLabel } from "elec/utils/normalizers"
import { memo } from "react"
import { useTranslation } from "react-i18next"
import { To } from "react-router-dom"

export interface ElecAdminProvisionCertificateTableProps {
  loading: boolean
  provisionCertificates: ElecProvisionCertificatePreview[]
  order: Order | undefined
  rowLink?: (provisionCertificate: ElecProvisionCertificatePreview) => To
  onOrder: (order: Order | undefined) => void
}

export const ElecAdminProvisionCertificateTable = memo(
  ({
    loading,
    provisionCertificates,
    order,
    rowLink,
    onOrder,
  }: ElecAdminProvisionCertificateTableProps) => {
    const columns = useColumns()
    return (
      <Table
        loading={loading}
        order={order}
        onOrder={onOrder}
        rowLink={rowLink}
        rows={provisionCertificates}
        columns={[
          columns.cpo,
          columns.quarter,
          columns.operating_unit,
          columns.source,
          columns.energy_amount,
        ]}
      />
    )
  }
)

export function useColumns() {
  const { t } = useTranslation()
  return {
    cpo: {
      key: "cpo",
      header: t("Aménageur"),
      cell: (provisionCertificate: ElecProvisionCertificatePreview) => {
        const value = provisionCertificate.cpo.name
        return <Cell text={value} />
      },
    },

    quarter: {
      key: "quarter",
      header: t("Trimestre"),
      cell: (provisionCertificate: ElecProvisionCertificatePreview) => {
        return (
          <Cell
            text={t("T{{quarter}} {{year}}", {
              quarter: provisionCertificate.quarter,
              year: provisionCertificate.year,
            })}
          />
        )
      },
    },

    operating_unit: {
      key: "operating_unit",
      header: t("Unité d'exploitation"),
      cell: (provisionCertificate: ElecProvisionCertificatePreview) => {
        return <Cell text={provisionCertificate.operating_unit} />
      },
    },
    source: {
      key: "source",
      header: t("Source"),
      cell: (provisionCertificate: ElecProvisionCertificatePreview) => {
        return (
          <Cell
            text={t(
              getElecProvisionCertificateSourceLabel(
                provisionCertificate.source
              )
            )}
          />
        )
      },
    },

    energy_amount: {
      key: "energy_amount",
      header: t("MWh"),
      cell: (provisionCertificate: ElecProvisionCertificatePreview) => {
        return (
          <Cell
            text={
              "+ " +
              formatNumber(provisionCertificate.energy_amount, {
                fractionDigits: 0,
              })
            }
          />
        )
      },
    },
  }
}

export default ElecAdminProvisionCertificateTable
