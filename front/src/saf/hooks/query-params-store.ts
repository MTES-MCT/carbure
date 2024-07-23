import { Entity } from "carbure/types"
import { useLimit } from "common/components/pagination"
import { Order } from "common/components/table"
import useStore from "common/hooks/store"
import useTitle from "common/hooks/title"
import { useTranslation } from "react-i18next"
import {
	SafClientSnapshot,
	SafFilterSelection,
	SafOperatorSnapshot,
	SafStates,
	SafTicketSourceStatus,
	SafTicketStatus,
	SafQueryType,
} from "saf/types"
import { useFilterSearchParams } from "./filter-search-params"

export function useQueryParamsStore(
	entity: Entity,
	year: number,
	status: SafTicketSourceStatus | SafTicketStatus,
	snapshot?: SafOperatorSnapshot | SafClientSnapshot,
	type?: SafQueryType
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
			search: undefined,
			invalid: false,
			deadline: false,
			order: undefined,
			selection: [],
			page: 0,
			limit,
			type,
		} as SafStates,
		{
			setEntity: (entity: Entity) => ({
				entity,
				filters: filtersParams,
				invalid: false,
				deadline: false,
				selection: [],
				page: 0,
			}),

			setYear: (year: number) => ({
				year,
				filters: filtersParams,
				invalid: false,
				deadline: false,
				selection: [],
				page: 0,
			}),

			setSnapshot: (snapshot: SafOperatorSnapshot | SafClientSnapshot) => ({
				snapshot,
				filters: filtersParams,
				invalid: false,
				deadline: false,
				selection: [],
				page: 0,
			}),

			setStatus: (status: SafTicketSourceStatus | SafTicketStatus) => {
				return {
					status,
					filters: filtersParams,
					invalid: false,
					deadline: false,
					selection: [],
					page: 0,
				}
			},

			setType: (type: SafQueryType) => {
				return {
					type,
					filters: filtersParams,
					selection: [],
					page: 0,
				}
			},

			setFilters: (filters: SafFilterSelection) => {
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

	if (type && state.type !== type) {
		actions.setType(type)
	}

	return [state, actions] as [typeof state, typeof actions]
}

export function usePageTitle(state: SafStates) {
	const { t } = useTranslation()

	const statuses: any = {
		[SafTicketSourceStatus.Available]: t("Volumes disponibles"),
		[SafTicketSourceStatus.History]: t("Volumes historiques"),
		[SafTicketStatus.Accepted]: t("Tickets acceptés"),
		[SafTicketStatus.Pending]: t("Tickets en attente"),
		[SafTicketStatus.Rejected]: t("Tickets refusés"),
	}

	const entity = state.entity.name
	const year = state.year
	const status = statuses[state.status.toUpperCase()]

	useTitle(`${entity} ∙ ${status} ${year}`)
}
