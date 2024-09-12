import { useState } from "react"
import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common/hooks/async"
import { Panel, Row } from "common/components/scaffold"
import { ChevronLeft, ChevronRight, Square } from "common/components/icons"
import Tabs from "common/components/tabs"
import Table, { Cell, Column } from "common/components/table"
import Select from "common/components/select"
import Button from "common/components/button"
import * as api from "../api"
import { DashboardDeclaration } from "dashboard/types"
import { groupBy, sortBy } from "common/utils/collection"
import { EntityType } from "carbure/types"
import { formatPeriod } from "common/utils/formatters"
import i18next from "i18next"
import { Link } from "react-router-dom"
import { normalizePeriod } from "carbure/utils/normalizers"
import NoResult from "common/components/no-result"

const date = new Date()
const currentPeriod = `${date.getFullYear() * 100 + date.getMonth() + 1}`

const Declarations = () => {
  const { t } = useTranslation()
  const entity = useEntity()

  const [focus, setFocus] = useState<string>(EntityType.Operator)
  const [period, setPeriod] = useState<string | undefined>(currentPeriod)

  const periods = useQuery(api.getPeriods, {
    key: "dashboard-periods",
    params: [entity.id],
  })

  const declarations = useQuery(api.getDeclarations, {
    key: "transactions-admin-declarations",
    params: [entity.id, period!],
  })

  const periodData = (periods.result ?? []).map(String).sort((a, b) => a < b ? 1 : -1) // prettier-ignore
  const declarationData = declarations.result?.data.data ?? []

  const groupedByEntityType = groupBy(
    declarationData,
    (d) => d.declaration.entity.entity_type
  )

  function movePeriod(direction: number) {
    if (!periodData) return
    const index = periodData.findIndex((p) => p === period)
    // we remove direction because the array is in antichronological order
    const newIndex = Math.max(0, Math.min(index - direction, periodData.length - 1)) // prettier-ignore
    setPeriod(periodData[newIndex])
  }

  return (
    <Panel>
      <header>
        <h1>{t("Déclarations")}</h1>
        <Legend />
      </header>
      <section>
        <Row style={{ alignItems: "center" }}>
          <Row style={{ gap: 8 }}>
            <Button icon={ChevronLeft} action={() => movePeriod(-1)} />
            <Select
              search
              loading={periods.loading}
              value={period}
              onChange={setPeriod}
              options={periodData}
              normalize={normalizePeriod}
              style={{ width: 200 }}
            />
            <Button icon={ChevronRight} action={() => movePeriod(+1)} />
          </Row>

          <Tabs
            focus={focus}
            onFocus={setFocus}
            style={{ marginLeft: "var(--spacing-l)" }}
            tabs={[
              { key: EntityType.Operator, label: t("Opérateur") },
              { key: EntityType.Producer, label: t("Producteur") },
              { key: EntityType.Trader, label: t("Trader") },
              {
                key: EntityType.PowerOrHeatProducer,
                label: t("Producteur d'électricité ou de chaleur"),
              },
            ]}
          />
        </Row>
      </section>

      {focus === EntityType.Operator && (
        <DeclarationTable
          period={period!}
          loading={declarations.loading}
          declarations={groupedByEntityType[EntityType.Operator]}
        />
      )}
      {focus === EntityType.Producer && (
        <DeclarationTable
          period={period!}
          loading={declarations.loading}
          declarations={groupedByEntityType[EntityType.Producer]}
        />
      )}
      {focus === EntityType.Trader && (
        <DeclarationTable
          period={period!}
          loading={declarations.loading}
          declarations={groupedByEntityType[EntityType.Trader]}
        />
      )}
      {focus === EntityType.PowerOrHeatProducer && (
        <DeclarationTable
          period={period!}
          loading={declarations.loading}
          declarations={groupedByEntityType[EntityType.PowerOrHeatProducer]}
        />
      )}
    </Panel>
  )
}

interface DeclarationTableProps {
  loading: boolean
  period: string
  declarations: DashboardDeclaration[] | undefined
}

const DeclarationTable = ({
  loading,
  period,
  declarations,
}: DeclarationTableProps) => {
  const { t } = useTranslation()

  if (!declarations || declarations.length === 0) {
    return (
      <>
        <section>
          <NoResult
            label={t("Aucune déclaration pour cette période")}
            loading={loading}
          />
        </section>
        <footer />
      </>
    )
  }

  const columns = getDeclarationDashboardColumns(period)
  const rows = getEntityDeclarationsByPeriod(declarations)

  return (
    <Table variant="compact" loading={loading} rows={rows} columns={columns} />
  )
}

const Legend = () => (
  <Row asideX style={{ gap: "var(--spacing-m)" }}>
    <Row style={{ alignItems: "center", gap: "var(--spacing-s)" }}>
      <Square size={16} color="var(--orange-medium)" />
      En cours
    </Row>

    <Row style={{ alignItems: "center", gap: "var(--spacing-s)" }}>
      <Square size={16} color="var(--red-dark)" />
      Relancé
    </Row>

    <Row style={{ alignItems: "center", gap: "var(--spacing-s)" }}>
      <Square size={16} color="var(--blue-dark)" />
      Déclaré par l'entité
    </Row>

    <Row style={{ alignItems: "center", gap: "var(--spacing-s)" }}>
      <Square size={16} color="var(--green-dark)" />
      Approuvé par l'administration
    </Row>
  </Row>
)

function getEntityDeclarationsByPeriod(declarations: DashboardDeclaration[]) {
  const groupedByEntity = groupBy(declarations, (d) => d.declaration.entity.id)
  const entityRows = Object.entries(groupedByEntity).map(
    ([_, declarations]) => ({
      entity: declarations[0]?.declaration.entity.name ?? i18next.t("Inconnu"),
      ...groupBy(declarations, (d) => d.declaration.period),
    })
  )

  return sortBy(entityRows, (d) => d.entity)
}

function getDeclarationDashboardColumns(period: string) {
  const entityColumn: Column<any> = {
    header: i18next.t("Entité") as string,
    cell: (d) => <Cell style={{ paddingLeft: 20 }} text={d.entity} />,
  }

  const periods = getPeriodsAround(period)
  const periodColumns: Column<any>[] = periods.map((period) => ({
    header: formatPeriod(period),
    cell: (row) => {
      const { count, declaration } = row[period]?.[0] ?? {}

      const year = Math.floor((declaration?.period ?? 0) / 100)

      const lotCount =
        (count?.drafts ?? 0) +
        (count?.input ?? 0) +
        (count?.output ?? 0) +
        (count?.corrections ?? 0)

      const params =
        declaration?.entity.entity_type === EntityType.Operator
          ? `clients=${declaration?.entity.name}`
          : `suppliers=${declaration?.entity.name}`

      return (
        <Link
          to={`../controls/${year}/declarations/?${params}&periods=${declaration?.period}`}
          style={{
            display: "block",
            height: 48,
            backgroundColor:
              lotCount === 0
                ? undefined
                : declaration?.declared
                  ? "var(--blue-dark)"
                  : "var(--orange-medium)",
          }}
        />
      )
    },
  }))

  return [entityColumn, ...periodColumns]
}

function getPeriodsAround(period: string) {
  const periodNum = parseInt(period)
  const periodYear = Math.floor(periodNum / 100)
  const periodMonth = periodNum % 100
  const prevMonth = periodMonth === 1 ? 12 : periodMonth - 1
  const prevYear = periodMonth === 1 ? periodYear - 1 : periodYear
  const nextMonth = periodMonth === 12 ? 1 : periodMonth + 1
  const nextYear = periodMonth === 12 ? periodYear + 1 : periodYear
  return [prevYear * 100 + prevMonth, period, nextYear * 100 + nextMonth]
}

export default Declarations
