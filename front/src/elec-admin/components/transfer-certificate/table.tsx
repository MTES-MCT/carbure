import Table, { Cell, Order } from "common/components/table"
import { formatDate } from "common/utils/formatters"
import { ElecTransferCertificatePreview } from "elec/types"

import { memo } from "react"
import { useTranslation } from "react-i18next"
import { To } from "react-router-dom"

export interface ElecAdminTransferCertificateTableProps {
    loading: boolean
    transferCertificates: ElecTransferCertificatePreview[]
    order: Order | undefined
    rowLink?: (provisionCertificate: ElecTransferCertificatePreview) => To
    onOrder: (order: Order | undefined) => void
    selected: number[]
    onSelect: (selected: number[]) => void
    // status: ElecAdminTransferCertificateStatu
}

export const ElecAdminTransferCertificateTable = memo(
    ({
        loading,
        transferCertificates,
        order,
        rowLink,
        onOrder,
        selected,
        onSelect,
        // status,
    }: ElecAdminTransferCertificateTableProps) => {
        const columns = useColumns()
        return (
            <Table
                loading={loading}
                order={order}
                onOrder={onOrder}
                rowLink={rowLink}
                rows={transferCertificates}
                columns={[
                    columns.cpo,
                    columns.transfer_date,
                    columns.operator,
                    columns.energy_amount,
                    columns.certificate_id,
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
            cell: (provisionCertificate: ElecTransferCertificatePreview) => {
                const value =
                    provisionCertificate.supplier.name
                return <Cell text={value} />
            },
        },
        operator: {
            key: "operator",
            header: t("Redevable"),
            cell: (provisionCertificate: ElecTransferCertificatePreview) => {
                const value =
                    provisionCertificate.client.name
                return <Cell text={value} />
            },
        },

        transfer_date: {
            key: "transfer_date",
            header: t("Date d'émission"),
            cell: (provisionCertificate: ElecTransferCertificatePreview) => {
                const value =
                    formatDate(provisionCertificate.transfer_date)
                return <Cell text={value} />
            },
        },
        energy_amount: {
            key: "energy_amount",
            header: t("MWh"),
            cell: (provisionCertificate: ElecTransferCertificatePreview) => {
                return (
                    <Cell
                        text={provisionCertificate.energy_amount}
                    />
                )
            },
        },
        certificate_id: {
            key: "certificate_id",
            header: t("Numéro"),
            cell: (provisionCertificate: ElecTransferCertificatePreview) => {
                return (
                    <Cell
                        text={provisionCertificate.certificate_id}
                    />
                )
            },
        },
    }
}

export default ElecAdminTransferCertificateTable
