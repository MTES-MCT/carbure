import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, Navigate, useParams } from "react-router-dom"
import * as api from "../../api"
import { Entity, UserRole } from "carbure/types"

import useEntity from "carbure/hooks/entity"

import { useQuery } from "common/hooks/async"
import { Order } from "common/components/table"
import { Bar } from "common/components/scaffold"
import Pagination, { useLimit } from "common/components/pagination"
import Filters, { useFilterParams } from "../filters"
import LotTable from "./lot-table"
import NoResult from "../../../transactions/components/no-result"
import LotActions from "./lot-actions"
import {
  DeadlineSwitch,
  InvalidSwitch,
} from "../../../transactions/components/switches"
import { LotSummaryBar } from "./lot-summary"
import SearchBar from "../../../transactions/components/search-bar"
import LotAdd from "lot-add"
import LotDetails from "transaction-details/components/lots"
import useStore from "common/hooks/store"
import { useMatomo } from "matomo"
import {
  getDefaultCategory,
  useAutoCategory,
} from "../../../transactions/components/category"
import useTitle from "common/hooks/title"
import { AdminStatus } from "controls/types"
import HashRoute from "common/components/hash-route"
import {
  FilterSelection,
  SafCertificateFilter,
  SafCertificateQuery,
  SafCertificateQueryStatus,
  SafCertificateStatus,
  SafSnapshot,
} from "saf-certificates/types"
import { useAutoStatus } from "../status"
import { useQueryParamsStore } from "saf-certificates/hooks/query-params-store"

export interface CertificatesProps {
  year: number
  snapshot: SafSnapshot | undefined
}

export const Certificates = ({ year, snapshot }: CertificatesProps) => {
  console.log("snapshot:", snapshot)
  // const matomo = useMatomo()
  const location = useLocation()

  const entity = useEntity()
  const status = useAutoStatus()

  const [state, actions] = useQueryParamsStore(entity, year, status, snapshot) // prettier-ignore
  // const query = useSafCertificateQuery(state)
  return null
  // const safCertificates = useQuery(api.getSafCertificates, {
  //   key: "saf_certificates",
  //   params: [query],

  //   onSuccess: () => {
  //     if (state.selection.length > 0) {
  //       actions.setSelection([])
  //     }
  //   },
  // })

  // const safCertificatesData = safCertificates.result?.data.data
  // const safCertificateList = safCertificatesData?.saf_certificates ?? []
  // const ids = safCertificatesData?.ids ?? []
  // const count = safCertificatesData?.returned ?? 0
  // const total = safCertificatesData?.total ?? 0

  // const trackShowLotDetails = (lot: Lot) => {
  //   matomo.push(["trackEvent", "lots-details", "show-lot-details", lot.id])
  // }

  // const showLotDetails = (lot: Lot) => ({
  //   pathname: location.pathname,
  //   search: location.search,
  //   hash: `lot/${lot.id}`,
  // })

  // if (category === undefined) {
  //   const defaultCategory = getDefaultCategory(status, snapshot)
  //   return <Navigate to={`${status}/${defaultCategory}`} />
  // }

  // return (
  //   <>
  //     <Bar>
  //       {/* <Filters
  //         query={query}
  //         filters={filtersByStatus[status]}
  //         selected={state.filters}
  //         onSelect={actions.setFilters}
  //         getFilters={api.getLotFilters}
  //       /> */}
  //     </Bar>

  //     <section>
  //       {/* <SearchBar
  //         count={snapshot?.lots}
  //         search={state.search}
  //         category={state.category}
  //         query={query}
  //         selection={state.selection}
  //         onSearch={actions.setSearch}
  //         onSwitch={actions.setCategory}
  //       />

  //       {entity.hasRights(UserRole.Admin, UserRole.ReadWrite) && (
  //         <LotActions
  //           count={count}
  //           category={state.category}
  //           query={query}
  //           selection={state.selection}
  //         />
  //       )}

  //       {count === 0 && (
  //         <NoResult
  //           loading={lots.loading}
  //           filters={state.filters}
  //           onFilter={actions.setFilters}
  //         />
  //       )} */}

  //       {count > 0 && (
  //         <>
  //           {/* <LotSummaryBar
  //             query={query}
  //             selection={state.selection}
  //             filters={state.filters}
  //             onFilter={actions.setFilters}
  //           />

  //           <LotTable
  //             loading={lots.loading}
  //             order={state.order}
  //             lots={lotList}
  //             errors={lotErrors}
  //             selected={state.selection}
  //             rowLink={showLotDetails}
  //             onSelect={actions.setSelection}
  //             onAction={trackShowLotDetails}
  //             onOrder={actions.setOrder}
  //           />

  //           <Pagination
  //             page={state.page}
  //             limit={state.limit}
  //             total={total}
  //             onPage={actions.setPage}
  //             onLimit={actions.setLimit}
  //           /> */}
  //         </>
  //       )}
  //     </section>

  //     <HashRoute path="add" element={<LotAdd />} />
  //     <HashRoute path="lot/:id" element={<LotDetails neighbors={ids} />} />
  //   </>
  // )
}

// const DRAFT_FILTERS = [
//   Filter.Periods,
//   Filter.Biofuels,
//   Filter.Feedstocks,
//   Filter.CountriesOfOrigin,
//   Filter.Suppliers,
//   Filter.Clients,
//   Filter.ProductionSites,
//   Filter.DeliverySites,
// ]

// const IN_FILTERS = [
//   Filter.LotStatus,
//   Filter.DeliveryTypes,
//   Filter.Periods,
//   Filter.Biofuels,
//   Filter.Feedstocks,
//   Filter.CountriesOfOrigin,
//   Filter.Suppliers,
//   Filter.ProductionSites,
//   Filter.DeliverySites,
// ]

// const OUT_FILTERS = [
//   Filter.LotStatus,
//   Filter.Periods,
//   Filter.Biofuels,
//   Filter.Feedstocks,
//   Filter.CountriesOfOrigin,
//   Filter.Clients,
//   Filter.ClientTypes,
//   Filter.ProductionSites,
//   Filter.DeliverySites,
// ]

// const filtersByStatus: Record<Status, Filter[]> = {
//   drafts: DRAFT_FILTERS,
//   in: IN_FILTERS,
//   out: OUT_FILTERS,
//   stocks: [],
//   declaration: [],
//   unknown: [],
// }

// // export function useLotTitle(state: QueryParams) {
// //   const { t } = useTranslation()

// //   const statuses: Record<Status, string> = {
// //     drafts: t("brouillons"),
// //     in: t("lots reçus"),
// //     out: t("lots envoyés"),
// //     stocks: t("stocks"),
// //     declaration: "",
// //     unknown: "",
// //   }

// //   const adminStatuses: Record<AdminStatus, string> = {
// //     alerts: t("alertes"),
// //     lots: t("lots"),
// //     stocks: t("stocks"),
// //     unknown: "",
// //   }

// //   const categories: any = {
// //     pending: t("en attente"),
// //     correction: t("en correction"),
// //     history: "",
// //   }

// //   const entity = state.entity.name
// //   const year = state.year
// //   const status =
// //     state.status in statuses
// //       ? statuses[state.status]
// //       : adminStatuses[state.status as AdminStatus] ?? ""
// //   const category = state.status in statuses ? categories[state.category] : ""

// //   useTitle(`${entity} ∙ ${status} ${category} ${year}`)
// // }

// export function useSafCertificateQuery({
//   entity,
//   status,
//   category,
//   year,
//   search,
//   invalid,
//   deadline,
//   page = 0,
//   limit,
//   order,
//   filters,
// }: QueryParams) {
//   return useMemo<SafCertificateQuery>(
//     () => ({
//       entity_id: entity.id,
//       year,
//       status,
//       category,
//       query: search ? search : undefined,
//       history: category === "history" ? true : undefined,
//       correction: category === "correction" ? true : undefined,
//       invalid: invalid ? true : undefined,
//       deadline: deadline ? true : undefined,
//       from_idx: page * (limit ?? 0),
//       limit: limit || undefined,
//       sort_by: order?.column,
//       order: order?.direction,
//       ...filters,
//     }),
//     [
//       entity.id,
//       year,
//       status,
//       category,
//       search,
//       invalid,
//       limit,
//       order,
//       filters,
//       deadline,
//       page,
//     ]
//   )
// }

// export default Certificates
