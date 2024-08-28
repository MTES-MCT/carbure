import useEntity from "carbure/hooks/entity"
import HashRoute from "common/components/hash-route"
import NoResult from "common/components/no-result"
import Pagination from "common/components/pagination"
import { ActionBar, Bar } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"

import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder"
import FilterMultiSelect from "common/molecules/filter-select"
import {
  ElecAdminProvisionCertificateFilter,
  ElecAdminProvisionCertificateStates,
  ElecAdminProvisionCertificateStatus,
} from "./types"
import {
  ElecAdminSnapshot,
} from "elec-admin/types"
import { ElecProvisionCertificatePreview } from "elec/types"
import { useTranslation } from "react-i18next"
import { useLocation, useMatch } from "react-router-dom"
import * as api from "./api"
import ProvisionImportButton from "./Import"
import ElecAdminProvisionDetailsDialog from "./details"
import { usePageTitle } from "./page-title"
import { StatusSwitcher } from "./status-switcher"
import ElecAdminProvisionCertificateTable from "./table"

type ProvisionListProps = {
  snapshot: ElecAdminSnapshot
  year: number
}

const ProvisionList = ({ snapshot, year }: ProvisionListProps) => {
  const entity = useEntity()
  const status = useAutoStatus()
  const [state, actions] =
    useCBQueryParamsStore<ElecAdminProvisionCertificateStates>(
      entity,
      year,
      status,
      snapshot
    )
  usePageTitle(state)
  const query = useCBQueryBuilder(state)
  const location = useLocation()
  const { t } = useTranslation()

  const provisionCertificatesResponse = useQuery(api.getProvisionCertificates, {
    key: "elec-admin-provision-certificates",
    params: [query],
  })

  const showProvisionCertificateDetails = (
    provisionCertificate: ElecProvisionCertificatePreview
  ) => {
    return {
      pathname: location.pathname,
      search: location.search,
      hash: `provision-certificate/${provisionCertificate.id}`,
    }
  }

  const provisionCertificatesData =
    provisionCertificatesResponse.result?.data.data
  const total = provisionCertificatesData?.total ?? 0
  const count = provisionCertificatesData?.returned ?? 0

  const filterLabels = {
    [ElecAdminProvisionCertificateFilter.Cpo]: t("Aménageur"),
    [ElecAdminProvisionCertificateFilter.Quarter]: t("Trimestre"),
    [ElecAdminProvisionCertificateFilter.OperatingUnit]: t(
      "Unité d'exploitation"
    ),
  }

  return (
    <>
      <Bar>
        <FilterMultiSelect
          filterLabels={filterLabels}
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

          <ProvisionImportButton />
        </ActionBar>

        {count > 0 && provisionCertificatesData ? (
          <>
            <ElecAdminProvisionCertificateTable
              loading={provisionCertificatesResponse.loading}
              order={state.order}
              provisionCertificates={
                provisionCertificatesData.elec_provision_certificates
              }
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
          <NoResult loading={provisionCertificatesResponse.loading} />
        )}
      </section>
      <HashRoute
        path="provision-certificate/:id"
        element={<ElecAdminProvisionDetailsDialog />}
      />
    </>
  )
}
export default ProvisionList

export function useAutoStatus(): ElecAdminProvisionCertificateStatus {
  const matchStatus = useMatch("/org/:entity/elec-admin/:year/:view/:status/*")
  const status =
    matchStatus?.params?.status?.toUpperCase() as ElecAdminProvisionCertificateStatus
  return status ?? ElecAdminProvisionCertificateStatus.Available
}
