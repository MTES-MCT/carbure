import { Entity } from "carbure/types"
import { useLimit } from "common/components/pagination"
import { Order } from "common/components/table"
import useStore from "common/hooks/store"
import useTitle from "common/hooks/title"
import {
	ElecCPOSnapshot,
	ElecTransferCertificateFilterSelection,
	ElecTransferCertificateStates,
	ElecTransferCertificateStatus,
} from "elec/types-cpo"
import { useTranslation } from "react-i18next"
import { useFilterSearchParams } from "./transfer-certificate-filter-search-params"
import { ElecOperatorSnapshot, ElecOperatorStatus } from "elec/types-operator"

export function useTransferCertificateQueryParamsStore(
	entity: Entity,
	year: number,
	status: ElecTransferCertificateStatus | ElecOperatorStatus,
	snapshot?: ElecCPOSnapshot | ElecOperatorSnapshot
) {
	const [limit, saveLimit] = useLimit()
	const [filtersParams, setFiltersParams] = useFilterSearchParams()

	const [state, actions] = useStore(
		{
			entity,
			year,
			snapshot,
			status,
			filters: filtersParams,

			order: undefined,
			selection: [],
			page: 0,
			limit,
		} as ElecTransferCertificateStates,
		{
			setEntity: (entity: Entity) => ({
				entity,
				filters: filtersParams,

				selection: [],
				page: 0,
			}),

			setYear: (year: number) => ({
				year,
				filters: filtersParams,

				selection: [],
				page: 0,
			}),

			setSnapshot: (snapshot: ElecCPOSnapshot | ElecOperatorSnapshot) => ({
				snapshot,
				filters: filtersParams,

				selection: [],
				page: 0,
			}),

			setStatus: (
				status: ElecTransferCertificateStatus | ElecOperatorStatus
			) => {
				return {
					status,
					filters: filtersParams,

					selection: [],
					page: 0,
				}
			},

			setFilters: (filters: ElecTransferCertificateFilterSelection) => {
				setTimeout(() => {
					setFiltersParams(filters)
				})
				return {
					filters,
					selection: [],
					page: 0,
				}
			},

			setSearch: (search: string | undefined) => ({
				search,
				selection: [],
				page: 0,
			}),

			setOrder: (order: Order | undefined) => ({
				order,
			}),

			setSelection: (selection: number[]) => ({
				selection,
			}),

			setPage: (page?: number) => ({
				page,
				selection: [],
			}),

			setLimit: (limit?: number) => {
				saveLimit(limit)
				return {
					limit,
					selection: [],
					page: 0,
				}
			},
		}
	)

	// sync tab title with current state
	usePageTitle(state)

	// sync store state with entity set from above
	if (state.entity.id !== entity.id) {
		actions.setEntity(entity)
	}

	// sync store state with year set from above
	if (state.year !== year) {
		actions.setYear(year)
	}

	// // sync store state with status set in the route
	if (state.status !== status) {
		actions.setStatus(status)
	}

	if (snapshot && state.snapshot !== snapshot) {
		actions.setSnapshot(snapshot)
	}

	return [state, actions] as [typeof state, typeof actions]
}

export function usePageTitle(state: ElecTransferCertificateStates) {
	const { t } = useTranslation()

	const statuses: any = {
		[ElecTransferCertificateStatus.Pending]:
			t("Énergie cédée") + " " + t("en attente"),
		[ElecTransferCertificateStatus.Accepted]:
			t("Énergie cédée") + " " + t("acceptée"),
		[ElecTransferCertificateStatus.Rejected]:
			t("Énergie cédée") + " " + t("rejetée"),
	}
	const entity = state.entity.name
	const year = state.year
	const status = statuses[state.status.toUpperCase()]

	useTitle(`${entity} ∙ ${status} ${year}`)
}
