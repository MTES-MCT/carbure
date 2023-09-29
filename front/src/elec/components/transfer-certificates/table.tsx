import Table, { Cell, Order } from "common/components/table"
import { compact } from "common/utils/collection"
import { formatDate } from "common/utils/formatters"
import TransferCertificateTag from "elec/components/transfer-certificates/tag"
import { ElecTransferCertificatePreview } from "elec/types"
import { memo } from "react"
import { useTranslation } from "react-i18next"

export interface ElecTransferCertificateTableProps {
    displayCpo?: boolean
    loading: boolean
    transferCertificates: ElecTransferCertificatePreview[]
    order: Order | undefined
    onAction?: (transferCertificate: ElecTransferCertificatePreview) => void
    onOrder: (order: Order | undefined) => void
    selected: number[]
    onSelect: (selected: number[]) => void
}

export const ElecTransferCertificateTable = memo(
    ({
        loading,
        transferCertificates,
        order,
        onAction,
        onOrder,
        displayCpo = false,
    }: ElecTransferCertificateTableProps) => {
        const columns = useColumns()
        return (
            <Table
                loading={loading}
                order={order}
                onOrder={onOrder}
                onAction={onAction}
                rows={transferCertificates}
                columns={compact([
                    columns.status,
                    displayCpo ? columns.cpo : columns.operator,
                    columns.transfer_date,
                    columns.energy_amount,
                    columns.certificate_id,
                ])}
            />
        )
    }
)

export function useColumns() {
    const { t } = useTranslation()
    return {
        status: {
            key: "status",
            header: t("Statut"),
            cell: (transferCertificate: ElecTransferCertificatePreview) => {
                return (
                    <TransferCertificateTag status={transferCertificate.status} />
                )
            },
        },

        operator: {
            key: "operator",
            header: t("Redevable"),
            cell: (transferCertificate: ElecTransferCertificatePreview) => {
                const value =
                    transferCertificate.client.name
                return <Cell text={value} />
            },
        },

        cpo: {
            key: "cpo",
            header: t("Aménegeur"),
            cell: (transferCertificate: ElecTransferCertificatePreview) => {
                const value =
                    transferCertificate.supplier.name
                return <Cell text={value} />
            },
        },

        transfer_date: {
            key: "transfer_date",
            header: t("Date d'émission"),
            cell: (transferCertificate: ElecTransferCertificatePreview) => {
                const value =
                    formatDate(transferCertificate.transfer_date)
                return <Cell text={value} />
            },
        },
        energy_amount: {
            key: "energy_amount",
            header: t("MWh"),
            cell: (transferCertificate: ElecTransferCertificatePreview) => {
                return (
                    <Cell
                        text={transferCertificate.energy_amount + " MWh"}
                    />
                )
            },
        },
        certificate_id: {
            key: "certificate_id",
            header: t("Numéro"),
            cell: (transferCertificate: ElecTransferCertificatePreview) => {
                return (
                    <Cell
                        text={transferCertificate.certificate_id}
                    />
                )
            },
        },
    }
}

export default ElecTransferCertificateTable
