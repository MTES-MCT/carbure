import { Button } from "common/components/button2"
import { SearchInput } from "common/components/inputs2"
import { ActionBar, Content, Main, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import useYears from "common/hooks/years-2"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"
import { getSupplyPlanInputs, getSupplyPlanYears } from "./api"
import useEntity from "common/hooks/entity"
import { useSupplyPlanColumns } from "./supply-plan.hooks"
import { useQuery } from "common/hooks/async"
import { Table } from "common/components/table2"
import { NoResult } from "common/components/no-result2"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { Notice } from "common/components/notice"
import { declarationInterval } from "biomethane/utils"

export const SupplyPlan = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Mes plans d'approvisionnement"))
  const entity = useEntity()
  const years = useYears("biomethane/supply-plan", () =>
    getSupplyPlanYears(entity.id)
  )
  const columns = useSupplyPlanColumns()
  const { result: supplyInputs, loading } = useQuery(getSupplyPlanInputs, {
    key: `supply-plan-inputs-${entity.id}-${years.selected}`,
    params: [entity.id, years.selected],
  })
  const selectedYearIsInCurrentInterval =
    years.selected === declarationInterval.year

  return (
    <Main>
      <Row>
        <Select
          options={years.options}
          value={years.selected}
          onChange={years.setYear}
        />
        <Button onClick={() => {}} iconId="ri-upload-line" asideX>
          {t("Valider mes informations annuelles")}
        </Button>
      </Row>
      <Content marginTop>
        <ActionBar>
          <ActionBar.Grow>
            <SearchInput />
          </ActionBar.Grow>
          <Button
            onClick={() => {}}
            iconId="ri-add-line"
            asideX
            priority="secondary"
          >
            {t("Ajouter un intrant")}
          </Button>
        </ActionBar>
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
        {!loading && !supplyInputs && <NoResult />}
        {supplyInputs && supplyInputs.results?.length > 0 && (
          <>
            <RecapQuantity
              text={t("{{total}} tonnes annuelles", {
                total: supplyInputs.annual_volumes_in_t,
              })}
            />
            <Table
              rows={supplyInputs.results}
              columns={columns}
              loading={loading}
            />
          </>
        )}
      </Content>
    </Main>
  )
}
