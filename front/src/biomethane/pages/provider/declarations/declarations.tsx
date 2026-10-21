import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router-dom"
import { useQuery } from "common/hooks/async"
import { Table } from "common/components/table2"
import { NoResult } from "common/components/no-result2"
import { Pagination } from "common/components/pagination2"
import { useQueryBuilder } from "common/hooks/query-builder-2"
import { Content, LoaderOverlay, Main } from "common/components/scaffold"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { SelectYearsAdmin } from "biomethane/pages/admin/components/select-years-admin"
import { getBiomethaneProviderDeclarations } from "../api"
import { BiomethaneProviderDeclarationsQueryBuilder } from "../types"
import { useProviderDeclarationsColumns } from "./declarations.hooks"

const currentYear = new Date().getFullYear()

const ProviderDeclarations = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Déclarations"))
  const columns = useProviderDeclarationsColumns()
  const { year: selectedYear } = useParams<"year">()
  const { state, actions, query } = useQueryBuilder<
    BiomethaneProviderDeclarationsQueryBuilder["config"]
  >({
    year: selectedYear ? Number.parseInt(selectedYear, 10) : currentYear,
  })

  const { result: declarations, loading } = useQuery(
    getBiomethaneProviderDeclarations,
    {
      key: "biomethane-provider-declarations",
      params: [query],
    }
  )

  return (
    <Main>
      <Content>
        <SelectYearsAdmin urlRoot="biomethane/provider/declarations" />
        {!loading && declarations && (
          <RecapQuantity
            text={t("{{count}} déclarations", {
              count: declarations.count,
            })}
          />
        )}
        {!loading && (!declarations || declarations.count === 0) && (
          <NoResult />
        )}
        {declarations && declarations.count > 0 && (
          <>
            <Table
              rows={declarations.results ?? []}
              columns={columns}
              loading={loading}
            />
            <Pagination
              defaultPage={query.page}
              total={declarations.count}
              limit={state.limit}
              onLimit={actions.setLimit}
              disabled={loading}
            />
          </>
        )}
        {loading && <LoaderOverlay />}
      </Content>
    </Main>
  )
}

export default ProviderDeclarations
