import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, Navigate } from "react-router-dom"
import * as api from "../../api"
import { Entity, UserRole } from "carbure/types"
import {
  Lot,
  Snapshot,
  FilterSelection,
  Status,
  LotQuery,
  Filter,
} from "../../../transactions/types"
import useEntity from "carbure/hooks/entity"
import { useAutoStatus } from "../../../transactions/components/status"
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
  SafCertificateFilter,
  SafCertificateQuery,
  SafCertificateStatus,
  SafSnapshot,
} from "saf-certificates/types"

export interface CertificatesProps {
  year: number
  snapshot: SafSnapshot | undefined
}

export const Certificates = ({ year, snapshot }: CertificatesProps) => {
  console.log("snapshot:", snapshot)
  const matomo = useMatomo()
  const location = useLocation()
  return null
  // const entity = useEntity()
  // const status = useAutoStatus()
  // const category = useAutoCategory(status, snapshot)

  // const [state, actions] = useQueryParamsStore(entity, year, status, category, snapshot) // prettier-ignore
  // const query = useSafCertificateQuery(state)

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

const DRAFT_FILTERS = [
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.Clients,
  Filter.ProductionSites,
  Filter.DeliverySites,
]

const IN_FILTERS = [
  Filter.LotStatus,
  Filter.DeliveryTypes,
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Suppliers,
  Filter.ProductionSites,
  Filter.DeliverySites,
]

const OUT_FILTERS = [
  Filter.LotStatus,
  Filter.Periods,
  Filter.Biofuels,
  Filter.Feedstocks,
  Filter.CountriesOfOrigin,
  Filter.Clients,
  Filter.ClientTypes,
  Filter.ProductionSites,
  Filter.DeliverySites,
]

const filtersByStatus: Record<Status, Filter[]> = {
  drafts: DRAFT_FILTERS,
  in: IN_FILTERS,
  out: OUT_FILTERS,
  stocks: [],
  declaration: [],
  unknown: [],
}

export interface QueryParams {
  entity: Entity
  year: number
  status: Status
  category?: string
  filters: SafCertificateFilter
  search: string | undefined
  invalid: boolean
  deadline: boolean
  selection: number[]
  page: number
  limit: number | undefined
  order: Order | undefined
  snapshot: Snapshot | undefined
}

// export function useQueryParamsStore(
//   entity: Entity,
//   year: number,
//   status: string,
//   category?: string,
//   snapshot?: Snapshot | undefined
// ) {
//   const [limit, saveLimit] = useLimit()
//   const [filtersParams, setFiltersParams] = useFilterParams()

//   const [state, actions] = useStore(
//     {
//       entity,
//       year,
//       snapshot,
//       status,
//       category: getDefaultCategory(status, snapshot),
//       filters: filtersParams,
//       search: undefined,
//       invalid: false,
//       deadline: false,
//       order: undefined,
//       selection: [],
//       page: 0,
//       limit,
//     } as QueryParams,
//     {
//       setEntity: (entity: Entity) => (state) => ({
//         entity,
//         category: getDefaultCategory(state.status, state.snapshot),
//         filters: filtersParams,
//         invalid: false,
//         deadline: false,
//         selection: [],
//         page: 0,
//       }),

//       setYear: (year: number) => (state) => ({
//         year,
//         category: getDefaultCategory(state.status, state.snapshot),
//         filters: filtersParams,
//         invalid: false,
//         deadline: false,
//         selection: [],
//         page: 0,
//       }),

//       setSnapshot: (snapshot: Snapshot) => (state) => {
//         return {
//           snapshot,
//           category: getDefaultCategory(state.status, snapshot),
//           filters: filtersParams,
//           invalid: false,
//           deadline: false,
//           selection: [],
//           page: 0,
//         }
//       },

//       setStatus: (status: Status) => (state) => ({
//         status,
//         category: getDefaultCategory(status, state.snapshot),
//         filters: filtersParams,
//         invalid: false,
//         deadline: false,
//         selection: [],
//         page: 0,
//       }),

//       setCategory: (category: string) => ({
//         category,
//         filters: filtersParams,
//         invalid: false,
//         deadline: false,
//         selection: [],
//         page: 0,
//       }),

//       setFilters: (filters: FilterSelection) => {
//         setTimeout(() => {
//           setFiltersParams(filters)
//         })
//         return {
//           filters,
//           selection: [],
//           page: 0,
//         }
//       },

//       setSearch: (search: string | undefined) => ({
//         search,
//         selection: [],
//         page: 0,
//       }),

//       setInvalid: (invalid: boolean) => ({
//         invalid,
//         selection: [],
//         page: 0,
//       }),

//       setDeadline: (deadline: boolean) => ({
//         deadline,
//         selection: [],
//         page: 0,
//       }),

//       setOrder: (order: Order | undefined) => ({
//         order,
//       }),

//       setSelection: (selection: number[]) => ({
//         selection,
//       }),

//       setPage: (page?: number) => ({
//         page,
//         selection: [],
//       }),

//       setLimit: (limit?: number) => {
//         saveLimit(limit)
//         return {
//           limit,
//           selection: [],
//           page: 0,
//         }
//       },
//     }
//   )

//   // sync tab title with current state
//   // useLotTitle(state)

//   // sync store state with entity set from above
//   if (state.entity.id !== entity.id) {
//     actions.setEntity(entity)
//   }

//   // sync store state with year set from above
//   if (state.year !== year) {
//     actions.setYear(year)
//   }

//   // sync store state with status set in the route
//   if (state.status !== status) {
//     actions.setStatus(status as Status)
//   }

//   // sync store state with category set in the route
//   if (category && state.category !== category) {
//     actions.setCategory(category)
//   }

//   if (snapshot && state.snapshot !== snapshot) {
//     actions.setSnapshot(snapshot)
//   }

//   return [state, actions] as [typeof state, typeof actions]
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
