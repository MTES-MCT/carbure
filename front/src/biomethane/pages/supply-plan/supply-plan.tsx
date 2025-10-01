import { Button } from "common/components/button2"
import { SearchInput } from "common/components/inputs2"
import { ActionBar, Content, Main, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import useYears from "common/hooks/years-2"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import {
  getSupplyPlanInputs,
  getSupplyPlanYears,
  downloadSupplyPlan,
} from "./api"
import useEntity from "common/hooks/entity"
import { useGetFilterOptions, useSupplyPlanColumns } from "./supply-plan.hooks"
import { useQuery } from "common/hooks/async"
import { Table } from "common/components/table2"
import { NoResult } from "common/components/no-result2"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { Notice } from "common/components/notice"
import { declarationInterval } from "biomethane/utils"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { BiomethaneSupplyInputQueryBuilder } from "./types"
import { Pagination } from "common/components/pagination2"
import { ExportButton } from "common/components/export"
import { ExcelImportDialog } from "./supply-input-dialog"
import { usePortal } from "common/components/portal"

export const SupplyPlan = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  usePrivateNavigation(t("Mes plans d'approvisionnement"))
  const entity = useEntity()
  const years = useYears("biomethane/supply-plan", () =>
    getSupplyPlanYears(entity.id)
  )
  const columns = useSupplyPlanColumns()

  const { state, actions, query } = useQueryBuilder<
    BiomethaneSupplyInputQueryBuilder["config"]
  >({
    year: years.selected,
  })
  const { getFilterOptions, filterLabels, normalizers } =
    useGetFilterOptions(query)

  const { result: supplyInputs, loading } = useQuery(getSupplyPlanInputs, {
    key: `supply-plan-inputs-${entity.id}-${years.selected}`,
    params: [query],
  })
  const selectedYearIsInCurrentInterval =
    years.selected === declarationInterval.year

  const openExcelImportDialog = () => {
    portal((close) => <ExcelImportDialog onClose={close} />)
  }

  return (
    <Main>
      <Row>
        <Select
          options={years.options}
          value={years.selected}
          onChange={years.setYear}
        />
        <Button
          onClick={openExcelImportDialog}
          iconId="ri-upload-line"
          asideX
          disabled={!selectedYearIsInCurrentInterval}
        >
          {t("Charger un plan d'approvisionnement")}
        </Button>
      </Row>
      <Content marginTop>
        <ActionBar>
          <ActionBar.Grow>
            <SearchInput value={state.search} onChange={actions.setSearch} />
          </ActionBar.Grow>
          <Button
            onClick={() => {}}
            iconId="ri-add-line"
            asideX
            priority="secondary"
            disabled={!selectedYearIsInCurrentInterval}
          >
            {t("Ajouter un intrant")}
          </Button>
          <ExportButton query={query} download={downloadSupplyPlan} />
        </ActionBar>
        <FilterMultiSelect2
          filterLabels={filterLabels}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getFilterOptions}
          normalizers={normalizers}
        />
        {selectedYearIsInCurrentInterval && (
          <Notice variant="info" icon="ri-time-line" isClosable>
            {t(
              "A déclarer et mettre à jour une fois par an, avant le {{date}}",
              {
                date: `31/03/${years.selected + 1}`,
              }
            )}
          </Notice>
        )}
        {!loading && (!supplyInputs || supplyInputs?.count === 0) && (
          <NoResult />
        )}
        {supplyInputs && supplyInputs.count > 0 && (
          <>
            <RecapQuantity
              text={t("{{total}} tonnes annuelles", {
                total: supplyInputs.annual_volumes_in_t,
              })}
            />
            <Table
              rows={supplyInputs?.results ?? []}
              columns={columns}
              loading={loading}
            />
          </>
        )}

        {supplyInputs && supplyInputs.count > 0 && (
          <Pagination
            defaultPage={query.page}
            total={supplyInputs.count}
            limit={state.limit}
            onLimit={actions.setLimit}
            disabled={loading}
          />
        )}
      </Content>
    </Main>
  )
}
