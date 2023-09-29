import useEntity from "carbure/hooks/entity"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useTransferCertificateQueryParamsStore } from "elec/hooks/transfer-certificate-query-params-store"
import { useTransferCertificatesQuery } from "elec/hooks/transfer-certificates-query"
import { ElecCPOSnapshot, ElecCPOTransferCertificateStatus } from "elec/types-cpo"
import { useMatch } from "react-router-dom"
import * as api from "../../api-cpo"
import TransferCertificateFilters from "./filters"
import { StatusSwitcher } from "./cpo-status-switcher"
import ElecTransferCertificateTable from "./table"
import ElectTransferDetailsDialog from "elec/components/transfer-certificates/details"
import { usePortal } from "common/components/portal"
import { ElecTransferCertificateFilter, ElecTransferCertificatePreview } from "elec/types"


type CPOTransferCertificateListProps = {
    snapshot: ElecCPOSnapshot
    year: number
}

const CPOTransferCertificateList = ({ snapshot, year }: CPOTransferCertificateListProps) => {

    const entity = useEntity()
    const status = useAutoStatus()
    const [state, actions] = useTransferCertificateQueryParamsStore(entity, year, status, snapshot)
    const query = useTransferCertificatesQuery(state)
    const portal = usePortal()

    const transferCertificatesResponse = useQuery(api.getTransferCertificates, {
        key: "elec-transfer-certificates",
        params: [query],
    })

    const showTransferCertificateDetails = (transferCertificate: ElecTransferCertificatePreview) => {
        portal((close) => <ElectTransferDetailsDialog
            onClose={close}
            transfer_certificate={transferCertificate} />)

    }

    const transferCertificatesData = transferCertificatesResponse.result?.data.data


    const total = transferCertificatesData?.total ?? 0
    const count = transferCertificatesData?.returned ?? 0
    return (
        <>

            <Bar>
                <TransferCertificateFilters
                    filters={FILTERS}
                    selected={state.filters}
                    onSelect={actions.setFilters}
                    getFilterOptions={(filter) =>
                        api.getTransferCertificateFilters(filter, query)
                    }
                />
            </Bar>
            <section>


                <ActionBar>
                    <StatusSwitcher
                        status={status}
                        onSwitch={actions.setStatus}
                        snapshot={snapshot}
                    />

                </ActionBar>

                {count > 0 && transferCertificatesData ? (
                    <>
                        <ElecTransferCertificateTable
                            loading={transferCertificatesResponse.loading}
                            order={state.order}
                            transferCertificates={transferCertificatesData.elec_transfer_certificates}
                            onAction={showTransferCertificateDetails}
                            selected={state.selection}
                            onSelect={actions.setSelection}
                            onOrder={actions.setOrder}
                        />

                        {(state.limit || 0) < total && (
                            <Pagination
                                page={state.page}
                                limit={state.limit}
                                total={total}
                                onPage={actions.setPage}
                                onLimit={actions.setLimit}
                            />
                        )}
                    </>
                ) : (
                    <NoResult
                        loading={transferCertificatesResponse.loading}
                    />
                )}

            </section >



        </>
    )
}
export default CPOTransferCertificateList



const FILTERS = [
    ElecTransferCertificateFilter.Operator,
    ElecTransferCertificateFilter.TransferDate,
    ElecTransferCertificateFilter.CertificateId
]

export function useAutoStatus() {
    const matchStatus = useMatch("/org/:entity/elec/:year/:view/:status/*")
    const status = matchStatus?.params?.status?.toUpperCase() as ElecCPOTransferCertificateStatus
    return status ?? ElecCPOTransferCertificateStatus.Pending
}