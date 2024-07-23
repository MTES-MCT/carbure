import { MultiSelect, MultiSelectProps } from "common/components/multi-select"; // prettier-ignore
import { Grid } from "common/components/scaffold"
import { defaultNormalizer } from "common/utils/normalize"
import {
	ElecAdminAuditFilter,
	ElecAdminAuditFilterSelection,
} from "elec-audit-admin/types"
import { ElecAuditFilter, ElecAuditFilterSelection } from "elec-audit/types"
import { useTranslation } from "react-i18next"

export interface FiltersProps {
	filters: ElecAuditFilter[]
	selected: ElecAuditFilterSelection
	onSelect: (filters: ElecAuditFilterSelection) => void
	getFilterOptions: (filter: ElecAuditFilter) => Promise<any[]>
}

export function ElecAuditFilters({
	filters,
	selected,
	onSelect,
	getFilterOptions,
}: FiltersProps) {
	const { t } = useTranslation()

	const filterLabels = {
		[ElecAuditFilter.Cpo]: t("Aménageur"),
	}

	return (
		<Grid>
			{filters.map((filter) => {
				return (
					<FilterSelect
						key={filter}
						field={filter}
						placeholder={filterLabels[filter]}
						value={selected[filter]}
						onChange={(value) =>
							onSelect({ ...selected, [filter]: value ?? [] })
						}
						getOptions={() => getFilterOptions(filter)}
					/>
				)
			})}
		</Grid>
	)
}

export default ElecAuditFilters

export type FilterSelectProps = { field: ElecAuditFilter } & Omit<
	MultiSelectProps<string>,
	"options"
>

export const FilterSelect = ({
	field,
	value = [],
	onChange,
	...props
}: FilterSelectProps) => (
	<MultiSelect
		{...props}
		clear
		search
		variant="solid"
		value={value}
		onChange={onChange}
		normalize={defaultNormalizer}
		sort={(item) => (item.value === "UNKNOWN" ? "" : item.label)}
	/>
)
