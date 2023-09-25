import useEntity from "carbure/hooks/entity"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useTransferCertificateQueryParamsStore } from "elec/hooks/transfer-certificate-query-params-store"
import { useTransferCertificatesQuery } from "elec/hooks/transfer-certificates-query"
import { ElecCPOSnapshot, ElecCPOTransferCertificateFilter, ElecCPOTransferCertificateStatus, ElecTransferCertificatePreview } from "elec/types"
import { useMatch } from "react-router-dom"
import * as api from "../../api"
import TransferCertificateFilters from "./filters"
import { StatusSwitcher } from "./status-switcher"
import ElecCPOTransferCertificateTable from "./table"
import ElectTransferDetailsDialog from "elec-admin/components/transfer-certificate/details"
import { usePortal } from "common/components/portal"


type TransferCertificateListProps = {
    snapshot: ElecCPOSnapshot
    year: number
}

const TransferCertificateList = ({ snapshot, year }: TransferCertificateListProps) => {

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
            onTransferCancelled={() => console.log("ok")}
            status={status}
            transfer_certificate={transferCertificate} />)

    }

    const transferCertificatesData = transferCertificatesResponse.result?.data.data

    // const provisionCertificatesData = elecAdminTransferCertificateList //TOTEST  


    // const ids = provisionCertificatesData?.ids ?? []

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
                {/* <EnergyTransferSummary remainingVolume={snapshot.remaining_energy} /> */}

                {count > 0 && transferCertificatesData ? (
                    <>
                        <ElecCPOTransferCertificateTable
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
                    // filters={state.filters}
                    // onFilter={actions.setFilters}
                    />
                )}

            </section >



        </>
    )
}
export default TransferCertificateList



const FILTERS = [
    ElecCPOTransferCertificateFilter.Operator,
    ElecCPOTransferCertificateFilter.TransferDate,
    ElecCPOTransferCertificateFilter.CertificateId
]

export function useAutoStatus() {
    const matchStatus = useMatch("/org/:entity/elec/:year/:view/:status/*")
    const status = matchStatus?.params?.status?.toUpperCase() as ElecCPOTransferCertificateStatus
    return status ?? ElecCPOTransferCertificateStatus.Pending
}