import Table, { Cell, Order } from "common/components/table"
import { formatDate } from "common/utils/formatters"
import { ElecCPOTransferCertificateStatus, ElecTransferCertificatePreview } from "elec/types"
import { memo } from "react"
import { useTranslation } from "react-i18next"
import { To } from "react-router-dom"

export interface ElecCPOTransferCertificateTableProps {
    loading: boolean
    provisionCertificates: ElecTransferCertificatePreview[]
    order: Order | undefined
    rowLink?: (provisionCertificate: ElecTransferCertificatePreview) => To
    onOrder: (order: Order | undefined) => void
    selected: number[]
    onSelect: (selected: number[]) => void
    status: ElecCPOTransferCertificateStatus
}

export const ElecCPOTransferCertificateTable = memo(
    ({
        loading,
        provisionCertificates,
        order,
        rowLink,
        onOrder,
        selected,
        onSelect,
        status,
    }: ElecCPOTransferCertificateTableProps) => {
        const columns = useColumns()
        return (
            <Table
                loading={loading}
                order={order}
                onOrder={onOrder}
                rowLink={rowLink}
                rows={provisionCertificates}
                columns={[
                    columns.operator,
                    columns.transfer_date,
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

export default ElecCPOTransferCertificateTable
