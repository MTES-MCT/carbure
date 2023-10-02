import useEntity from "carbure/hooks/entity"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { usePortal } from "common/components/portal"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import ElectTransferDetailsDialog from "elec/components/transfer-certificates/details"
import { useTransferCertificateQueryParamsStore } from "elec/hooks/transfer-certificate-query-params-store"
import { useTransferCertificatesQuery } from "elec/hooks/transfer-certificates-query"
import { ElecTransferCertificateFilter, ElecTransferCertificatePreview } from "elec/types"
import { ElecCPOTransferCertificateStatus } from "elec/types-cpo"
import { ElecOperatorSnapshot, ElecOperatorStatus } from "elec/types-operator"
import { useMatch } from "react-router-dom"
import * as api from "../../api-operator"
import TransferCertificateFilters from "./filters"
import ElecTransferCertificateTable from "./table"
import Button from "common/components/button"
import { Download } from "common/components/icons"
import { useTranslation } from "react-i18next"


type OperatorTransferCertificateListProps = {
    snapshot: ElecOperatorSnapshot
    year: number
}

const OperatorTransferCertificateList = ({ snapshot, year }: OperatorTransferCertificateListProps) => {

    const entity = useEntity()
    const status = useAutoStatus()
    const [state, actions] = useTransferCertificateQueryParamsStore(entity, year, status, snapshot)
    const query = useTransferCertificatesQuery(state)
    const portal = usePortal()
    const { t } = useTranslation()

    const transferCertificatesResponse = useQuery(api.getTransferCertificates, {
        key: "elec-transfer-certificates",
        params: [query],
    })

    const showTransferCertificateDetails = (transferCertificate: ElecTransferCertificatePreview) => {
        portal((close) => <ElectTransferDetailsDialog
            displayCpo={true}
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


                    {count > 0 && state.status === ElecOperatorStatus.Accepted &&

                        <Button
                            asideX={true}
                            icon={Download}
                            label={t("Exporter vers Excel")}
                            action={() => api.downloadTransferCertificates(query)
                            }
                        />
                    }

                </ActionBar>

                {count > 0 && transferCertificatesData ? (
                    <>
                        <ElecTransferCertificateTable
                            displayCpo={true}
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
export default OperatorTransferCertificateList



const FILTERS = [
    ElecTransferCertificateFilter.TransferDate,
    ElecTransferCertificateFilter.Cpo,
    ElecTransferCertificateFilter.CertificateId
]

export function useAutoStatus() {
    const matchStatus = useMatch("/org/:entity/elec/:year/:status/*")
    const status = matchStatus?.params?.status?.toUpperCase() as ElecOperatorStatus
    return status ?? ElecOperatorStatus.Pending
}