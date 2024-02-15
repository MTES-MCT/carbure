import Table, { Cell, Order } from "common/components/table"
import { formatNumber } from "common/utils/formatters"
import { ElecAdminProvisionCertificateStatus } from "elec-admin/types"
import { ElecProvisionCertificatePreview } from "elec/types"
import { memo } from "react"
import { useTranslation } from "react-i18next"
import { To } from "react-router-dom"

export interface ElecAdminProvisionCertificateTableProps {
    loading: boolean
    provisionCertificates: ElecProvisionCertificatePreview[]
    order: Order | undefined
    rowLink?: (provisionCertificate: ElecProvisionCertificatePreview) => To
    onOrder: (order: Order | undefined) => void
    selected: number[]
    onSelect: (selected: number[]) => void
    status: ElecAdminProvisionCertificateStatus
}

export const ElecAdminProvisionCertificateTable = memo(
    ({
        loading,
        provisionCertificates,
        order,
        rowLink,
        onOrder,
        selected,
        onSelect,
        status,
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
                    columns.current_type,
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
                const value =
                    provisionCertificate.cpo.name
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
                return (
                    <Cell
                        text={provisionCertificate.operating_unit}

                    />
                )
            },
        },
        current_type: {
            key: "current_type",
            header: t("Type de courant"),
            cell: (provisionCertificate: ElecProvisionCertificatePreview) => {
                return (
                    <Cell
                        text={provisionCertificate.current_type}

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
                        text={"+ " + formatNumber(provisionCertificate.energy_amount, 3)}
                    />
                )
            },
        },
    }
}

export default ElecAdminProvisionCertificateTable
