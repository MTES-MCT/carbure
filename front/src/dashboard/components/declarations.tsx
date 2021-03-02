import { useEffect, useState } from "react"
import cl from "clsx"
import { DeclarationsByMonth } from "../api"
import { Declaration, Entity, EntityType } from "common/types"
import { Box, LoaderOverlay, Title } from "common/components"
import Table, { Row } from "common/components/table"
import { Section, SectionHeader } from "common/components/section"
import { padding } from "transactions/components/list-columns"
import styles from "./declarations.module.css"
import { useRelativePush } from "common/components/relative-route"
import useAPI from "common/hooks/use-api"
import { Bell, Check, Cross } from "common/components/icons"
import * as api from "../api"
import { confirm } from "common/components/dialog"

type RowData = { entity: Entity; declarations: DeclarationsByMonth }

const entityColumn = {
  render: (v: RowData) => v.entity.name,
}

enum Evaluation {
  Checked,
  Declared,
  InProgress,
  Reminded,
  Idle,
}

function evaluateDeclaration(declaration: Declaration) {
  if (declaration.checked) {
    return Evaluation.Checked
  } else if (declaration.declared) {
    return Evaluation.Declared
  } else if (declaration.reminder_count > 0) {
    return Evaluation.Reminded
  } else if (Object.values(declaration.lots).some((v) => v > 0)) {
    return Evaluation.InProgress
  } else {
    return Evaluation.Idle
  }
}

function renderMonthSummary(
  month: string,
  askCheck: (d: Declaration, t: boolean) => Promise<any>,
  sendReminder: (d: Declaration) => Promise<any>
) {
  return (v: RowData) => {
    const relativePush = useRelativePush()

    const decl = v.declarations[month]

    if (!decl) return "N/A"

    const { drafts, validated, received, corrections } = decl.lots
    const ev = evaluateDeclaration(decl)

    const pushToTransactions = () =>
      relativePush(`../transactions/declaration`, {
        entity: v.entity,
        period: month.replace("/", "-"),
      })

    return (
      <Box
        row
        onClick={pushToTransactions}
        className={cl(
          styles.declarationCell,
          ev === Evaluation.Checked && styles.declarationChecked,
          ev === Evaluation.Declared && styles.declarationDeclared,
          ev === Evaluation.InProgress && styles.declarationInProgress,
          ev === Evaluation.Reminded && styles.declarationReminded
        )}
      >
        <ul className={styles.declarationSummary}>
          <li>
            {drafts ?? 0} brouillon{drafts !== 1 && "s"}
          </li>
          <li>
            {validated ?? 0} envoyé{validated !== 1 && "s"}
          </li>
          <li>
            {received ?? 0} reçu{received !== 1 && "s"}
          </li>
          <li>
            {corrections ?? 0} correction{corrections !== 1 && "s"}
          </li>
        </ul>

        {[Evaluation.InProgress, Evaluation.Reminded].includes(ev) && (
          <Bell
            className={styles.declarationValidation}
            title={`Relancer l'utilisateur (fait ${decl.reminder_count} fois)`}
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              sendReminder(decl)
            }}
          />
        )}

        {ev === Evaluation.Declared && (
          <Check
            className={styles.declarationValidation}
            title="Valider la déclaration"
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              askCheck(decl, true)
            }}
          />
        )}

        {ev === Evaluation.Checked && (
          <Cross
            className={styles.declarationValidation}
            title="Annuler la déclaration"
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              askCheck(decl, false)
            }}
          />
        )}
      </Box>
    )
  }
}

type DeclarationTableProps = {
  declarations: api.DeclarationsByEntities
  months: string[]
  entities: Entity[]
  onCheck: (d: Declaration, t: boolean) => Promise<any>
  onRemind: (d: Declaration) => Promise<any>
}

const DeclarationTable = ({
  declarations,
  months,
  entities,
  onCheck,
  onRemind,
}: DeclarationTableProps) => {
  const columns = months?.map((month) => ({
    header: month,
    render: renderMonthSummary(month, onCheck, onRemind),
  }))

  const rows: Row<RowData>[] = entities
    .filter((e) => e.id in declarations)
    .map((e) => ({
      value: {
        entity: e,
        declarations: declarations[e.id],
      },
    }))

  return (
    <Table
      className={styles.declarationTable}
      columns={[padding, entityColumn, ...columns]}
      rows={rows}
    />
  )
}

const Declarations = () => {
  const [focus, setFocus] = useState(EntityType.Producer)
  const [declarations, getDeclarations] = useAPI(api.getDeclarations)
  const [, checkDeclaration] = useAPI(api.checkDeclaration)
  const [, uncheckDeclaration] = useAPI(api.uncheckDeclaration)
  const [, sendReminder] = useAPI(api.sendDeclarationReminder)

  async function askDeclarationCheck(
    declaration: Declaration,
    toggle: boolean
  ) {
    const ok = await confirm(
      toggle ? "Validation déclaration" : "Annulation déclaration",
      toggle
        ? "Voulez-vous valider cette déclaration ?"
        : "Voulez-vous annuler la validation de cette déclaration ?"
    )

    if (ok) {
      if (toggle) {
        await checkDeclaration(declaration.id)
      } else {
        await uncheckDeclaration(declaration.id)
      }

      await getDeclarations()
    }
  }

  async function askSendReminder(declaration: Declaration) {
    const period = `${declaration.year}/${("0" + declaration.month).slice(-2)}`

    const ok = await confirm(
      "Relance déclaration",
      `Voulez-vous relancer ${declaration.entity.name} pour la période du ${period} ?`
    )

    if (ok) {
      await sendReminder(
        declaration.entity.id,
        declaration.year,
        declaration.month
      )

      await getDeclarations()
    }
  }

  useEffect(() => {
    getDeclarations()
  }, [getDeclarations])

  const [entities = [], months = [], byEntityType = {}] =
    declarations.data ?? []

  return (
    <Section>
      <SectionHeader>
        <Title>Résumé des déclarations</Title>
      </SectionHeader>

      <Box row>
        {[EntityType.Producer, EntityType.Trader, EntityType.Operator].map(
          (type) => (
            <span
              key={type}
              onClick={() => setFocus(type)}
              className={cl(
                styles.declarationFocus,
                type === focus && styles.declarationCurrentFocus
              )}
            >
              {type}s
            </span>
          )
        )}
      </Box>

      {focus === EntityType.Producer && (
        <DeclarationTable
          entities={entities}
          months={months}
          declarations={byEntityType[EntityType.Producer]}
          onCheck={askDeclarationCheck}
          onRemind={askSendReminder}
        />
      )}

      {focus === EntityType.Trader && (
        <DeclarationTable
          entities={entities}
          months={months}
          declarations={byEntityType[EntityType.Trader]}
          onCheck={askDeclarationCheck}
          onRemind={askSendReminder}
        />
      )}

      {focus === EntityType.Operator && (
        <DeclarationTable
          entities={entities}
          months={months}
          declarations={byEntityType[EntityType.Operator]}
          onCheck={askDeclarationCheck}
          onRemind={askSendReminder}
        />
      )}

      {declarations.loading && <LoaderOverlay />}
    </Section>
  )
}

export default Declarations
