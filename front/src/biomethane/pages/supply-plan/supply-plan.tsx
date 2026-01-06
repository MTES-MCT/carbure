import { Button } from "common/components/button2"
import { SearchInput } from "common/components/inputs2"
import { ActionBar, Row } from "common/components/scaffold"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { getSupplyPlanInputs, downloadSupplyPlan } from "./api"
import { useGetFilterOptions, useSupplyPlanColumns } from "./supply-plan.hooks"
import { useQuery } from "common/hooks/async"
import { Table } from "common/components/table2"
import { NoResult } from "common/components/no-result2"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { BiomethaneSupplyInputQueryBuilder } from "./types"
import { Pagination } from "common/components/pagination2"
import HashRoute from "common/components/hash-route"
import {
  CreateSupplyInputDialog,
  SupplyInputDialog,
} from "./supply-input-dialog"
import { ExportButton } from "common/components/export"
import { ExcelImportDialog } from "./supply-excel-import-dialog"
import { usePortal } from "common/components/portal"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

export const SupplyPlan = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  usePrivateNavigation(t("Mes plans d'approvisionnement"))
  const { selectedYear, canEditDeclaration } = useAnnualDeclaration()
  const columns = useSupplyPlanColumns()

  const { state, actions, query } = useQueryBuilder<
    BiomethaneSupplyInputQueryBuilder["config"]
  >({
    year: selectedYear,
  })
  const { getFilterOptions, filterLabels, normalizers } =
    useGetFilterOptions(query)

  const { result: supplyInputs, loading } = useQuery(getSupplyPlanInputs, {
    key: `supply-plan-inputs`,
    params: [query],
  })

  const openCreateSupplyInputDialog = () => {
    portal((close) => <CreateSupplyInputDialog onClose={close} />)
  }

  const openExcelImportDialog = () => {
    portal((close) => <ExcelImportDialog onClose={close} />)
  }

  return (
    <>
      <Row>
        <Button
          onClick={openExcelImportDialog}
          iconId="ri-upload-line"
          disabled={!canEditDeclaration}
          asideX
        >
          {t("Charger un plan d'approvisionnement")}
        </Button>
      </Row>

      <ActionBar>
        <ActionBar.Grow>
          <SearchInput value={state.search} onChange={actions.setSearch} />
        </ActionBar.Grow>
        <Button
          onClick={openCreateSupplyInputDialog}
          iconId="ri-add-line"
          asideX
          priority="secondary"
          disabled={!canEditDeclaration}
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
      {!loading && (!supplyInputs || supplyInputs?.count === 0) && <NoResult />}
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
            rowLink={(row) => ({
              pathname: location.pathname,
              search: location.search,
              hash: `supply-input/${row.id}`,
            })}
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
      <HashRoute path="/supply-input/:id" element={<SupplyInputDialog />} />
    </>
  )
}
