import cl from "clsx"
import { DeclarationsByMonth } from "../api"
import { Declaration, Entity } from "common/types"
import { LoaderOverlay, Title } from "common/components"
import Table, { Row } from "common/components/table"
import { Section, SectionHeader } from "common/components/section"
import { padding } from "transactions/components/list-columns"
import styles from "./declarations.module.css"
import { useRelativePush } from "common/components/relative-route"
import { ApiState } from "common/hooks/use-api"

type RowData = { entity: Entity; declarations: DeclarationsByMonth }

const entityColumn = {
  render: (v: RowData) => v.entity.name,
}

enum Evaluation {
  Checked = 0,
  Declared = 1,
  InProgress = 2,
  Idle = 3,
}

function evaluateMonth(
  declaration: Declaration | null
): Evaluation | undefined {
  if (!declaration) return

  if (declaration.checked) {
    return Evaluation.Checked
  } else if (declaration.declared) {
    return Evaluation.Declared
  } else if (Object.values(declaration.lots).some((v) => v > 0)) {
    return Evaluation.InProgress
  } else {
    return Evaluation.Idle
  }
}

function renderMonthSummary(month: string) {
  return (v: RowData) => {
    const relativePush = useRelativePush()
    const ev = evaluateMonth(v.declarations[month])

    const pushToTransactions = () =>
      relativePush(`../transactions/declaration`, {
        entity: v.entity,
        period: month.replace("/", "-"),
      })

    return (
      <ul
        onClick={pushToTransactions}
        className={cl(
          styles.declarationCell,
          ev === Evaluation.Checked && styles.declarationChecked,
          ev === Evaluation.Declared && styles.declarationDeclared,
          ev === Evaluation.InProgress && styles.declarationInProgress,
          ev === Evaluation.Idle && styles.declarationIdle
        )}
      >
        <li>{v.declarations[month]?.lots.drafts ?? 0} brouillons</li>
        <li>{v.declarations[month]?.lots.validated ?? 0} envoyés</li>
        <li>{v.declarations[month]?.lots.received ?? 0} reçus</li>
        <li>{v.declarations[month]?.lots.corrections ?? 0} corrections</li>
      </ul>
    )
  }
}

type DeclarationsProps = {
  declarations: ApiState<
    [Entity[], string[], Record<number, Record<string, Declaration>>]
  >
}

const Declarations = ({ declarations }: DeclarationsProps) => {
  const [entities = [], months = [], declarationsByEntites = {}] =
    declarations.data ?? []

  const columns = months?.map((month) => ({
    header: month,
    render: renderMonthSummary(month),
  }))

  const rows: Row<RowData>[] = entities?.map((e) => ({
    value: {
      entity: e,
      declarations: declarationsByEntites[e.id],
    },
  }))

  return (
    <Section>
      <SectionHeader>
        <Title>Résumé des déclarations</Title>
      </SectionHeader>
      <Table
        className={styles.declarationTable}
        columns={[padding, entityColumn, ...columns]}
        rows={rows}
      />
      {declarations.loading && <LoaderOverlay />}
    </Section>
  )
}

export default Declarations
