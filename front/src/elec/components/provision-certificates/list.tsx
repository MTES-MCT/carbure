import useEntity from "carbure/hooks/entity"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useProvistionCertificateQueryParamsStore } from "elec/hooks/provision-certificate-query-params-store"
import { useProvisionCertificatesQuery } from "elec/hooks/provision-certificates-query"
import { ElecCPOProvisionCertificateFilter, ElecCPOProvisionCertificateStatus, ElecCPOSnapshot } from "elec/types-cpo"
import { useLocation, useMatch } from "react-router-dom"
import * as api from "../../api-cpo"
import ProvisionCertificateFilters from "./filters"
import { StatusSwitcher } from "./status-switcher"
import { ElecCPOProvisionCertificateTable } from "./table"
import { EnergyTransferSummary } from "./transfer-summary"
import { elecAdminProvisionCertificateList } from "elec/__test__/data"
import { ElecProvisionCertificatePreview } from "elec/types"
import HashRoute from "common/components/hash-route"
import ElecProvisionDetailsDialog from "./details"


type ProvisionCertificateListProps = {
    snapshot: ElecCPOSnapshot
    year: number
}

const ProvisionCertificateList = ({ snapshot, year }: ProvisionCertificateListProps) => {

    const entity = useEntity()
    const status = useAutoStatus()
    const [state, actions] = useProvistionCertificateQueryParamsStore(entity, year, status, snapshot)
    const query = useProvisionCertificatesQuery(state)
    const location = useLocation()
    const provisionCertificatesResponse = useQuery(api.getProvisionCertificates, {
        key: "elec-provision-certificates",
        params: [query],
    })

    const showProvisionCertificateDetails = (provisionCertificate: ElecProvisionCertificatePreview) => {
        return {
            pathname: location.pathname,
            search: location.search,
            hash: `provision-certificate/${provisionCertificate.id}`,
        }
    }

    const provisionCertificatesData = provisionCertificatesResponse.result?.data.data
    // const provisionCertificatesData = elecAdminProvisionCertificateList //TOTEST  


    // const ids = provisionCertificatesData?.ids ?? []

    const total = provisionCertificatesData?.total ?? 0
    const count = provisionCertificatesData?.returned ?? 0
    return (
        <>

            <Bar>
                <ProvisionCertificateFilters
                    filters={FILTERS}
                    selected={state.filters}
                    onSelect={actions.setFilters}
                    getFilterOptions={(filter) =>
                        api.getProvisionCertificateFilters(filter, query)
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
                <EnergyTransferSummary remainingEnergy={snapshot.remaining_energy} />

                {count > 0 && provisionCertificatesData ? (
                    <>
                        <ElecCPOProvisionCertificateTable
                            loading={provisionCertificatesResponse.loading}
                            order={state.order}
                            provisionCertificates={provisionCertificatesData.elec_provision_certificates}
                            rowLink={showProvisionCertificateDetails}
                            selected={state.selection}
                            onSelect={actions.setSelection}
                            onOrder={actions.setOrder}
                            status={status}
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
                        loading={provisionCertificatesResponse.loading}

                    />
                )}
            </section >

            <HashRoute path="provision-certificate/:id" element={<ElecProvisionDetailsDialog />} />


        </>
    )
}
export default ProvisionCertificateList


const FILTERS = [
    ElecCPOProvisionCertificateFilter.Quarter,
    ElecCPOProvisionCertificateFilter.OperatingUnit,
]


export function useAutoStatus() {
    const matchStatus = useMatch("/org/:entity/elec/:year/:view/:status/*")
    const status = matchStatus?.params?.status?.toUpperCase() as ElecCPOProvisionCertificateStatus
    return status ?? ElecCPOProvisionCertificateStatus.Available
}