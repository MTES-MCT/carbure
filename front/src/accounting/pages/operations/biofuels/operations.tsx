import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { OperationsFilter, OperationsQueryBuilder } from "accounting/types"
import { useTranslation } from "react-i18next"

import * as api from "accounting/api/biofuels/operations"
import { Table } from "common/components/table2"
import { useQuery } from "common/hooks/async"
import {
  useGetFilterOptions,
  useOperationsBiofuelsColumns,
} from "./operations.hooks"
import { Pagination } from "common/components/pagination2/pagination"
import HashRoute from "common/components/hash-route"
import { OperationDetail } from "./pages/operation-detail"
import { NoResult } from "common/components/no-result2"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { useUnit } from "common/hooks/unit"
import {
  DEFAULT_UNIT_OPERATION,
  FRACTION_DIGITS_LITERS,
} from "accounting/config"
import { ActionBar } from "common/components/scaffold"
import { ExportButton } from "common/components/export"
import { Notice } from "common/components/notice"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { Button } from "common/components/button2"
import { useLocation, useNavigate } from "react-router-dom"
import { OperationsExcelImportDialog } from "../operations-excel-import-dialog"

const OperationsBiofuels = () => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit(DEFAULT_UNIT_OPERATION)
  const { selectedEntityId } = useSelectedEntity()
  const navigate = useNavigate()
  const location = useLocation()
  const filterLabels = {
    [OperationsFilter.years]: t("Année"),
    [OperationsFilter.status]: t("Statut"),
    [OperationsFilter.operation]: t("Opération"),
    [OperationsFilter.depot]: t("Dépôts"),
    [OperationsFilter.sector]: t("Filière"),
    [OperationsFilter.customs_category]: t("Catégorie"),
    [OperationsFilter.biofuel]: t("Biocarburants"),
    [OperationsFilter.durability_period]: t("Période de durabilité"),
    [OperationsFilter.period]: t("Date de création"),
    [OperationsFilter.type]: t("Débit / Crédit"),
    [OperationsFilter.from_to]: t("Destinataire"),
  }
  const { state, actions, query } =
    useQueryBuilder<OperationsQueryBuilder["config"]>()

  const { result, loading } = useQuery(api.getOperations, {
    key: `operations`,
    params: [query, selectedEntityId],
  })

  const columns = useOperationsBiofuelsColumns({
    onClickSector: (sector) => {
      actions.setFilters({
        ...state.filters,
        sector: [sector],
      })
    },
  })

  const getFilterOptions = useGetFilterOptions(query, selectedEntityId)

  return (
    <>
      <ActionBar>
        <ExportButton query={query} download={api.downloadOperations} />
        <Button
          onClick={() => {
            navigate({ search: location.search, hash: "#import" })
          }}
          iconId="ri-upload-line"
          asideX
          priority="secondary"
        >
          {t("Importer des opérations")}
        </Button>
      </ActionBar>

      <FilterMultiSelect2
        filterLabels={filterLabels}
        selected={state.filters}
        onSelect={actions.setFilters}
        getFilterOptions={getFilterOptions}
      />
      {!loading &&
      result?.data?.results &&
      result?.data?.results?.length === 0 ? (
        <NoResult />
      ) : (
        <>
          <Notice noColor variant="warning" isClosable={true}>
            {t(
              'Vos opérations d\'incorporation et de mise à consommation de biocarburants obtiennent par défaut le statut "validé" dans le cadre de cette bêta.'
            )}
            <br />
            {t(
              "Ce comportement est temporaire, dans l’attente de l’implémentation du mécanisme officiel de validation par un tiers."
            )}
          </Notice>
          <RecapQuantity
            text={t("{{count}} opérations pour un total de {{total}}", {
              count: result?.data?.count ?? 0,
              total: formatUnit(result?.data?.total_quantity ?? 0, {
                fractionDigits: FRACTION_DIGITS_LITERS,
              }),
            })}
          />
          <Table
            columns={columns}
            rows={result?.data?.results ?? []}
            rowLink={(row) => ({
              pathname: location.pathname,
              search: location.search,
              hash: `operation/${row.id}`,
            })}
            loading={loading}
            order={state.order}
            onOrder={actions.setOrder}
          />
          <Pagination
            defaultPage={query.page}
            total={result?.data?.count ?? 0}
            limit={state.limit}
            onLimit={actions.setLimit}
            disabled={loading}
          />
        </>
      )}

      <HashRoute path="operation/:id" element={<OperationDetail />} />
      <HashRoute
        path="/import"
        element={
          <OperationsExcelImportDialog
            onClose={() => {
              navigate({ search: location.search, hash: "#" })
            }}
          />
        }
      />
    </>
  )
}

export default OperationsBiofuels
