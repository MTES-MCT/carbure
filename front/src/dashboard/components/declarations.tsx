import { useEffect } from "react"
import cl from "clsx"
import { DeclarationsByMonth } from "../api"
import { Declaration, Entity } from "common/types"
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

function renderMonthSummary(
  month: string,
  askCheck: (d: Declaration, t: boolean) => Promise<any>,
  sendReminder: (d: Declaration) => Promise<any>
) {
  return (v: RowData) => {
    const relativePush = useRelativePush()
    const decl = v.declarations[month]

    // has some lots in transit but nothing declared or approved by admin
    const isInProgress =
      Object.values(decl.lots).some((v) => v > 0) &&
      !decl.checked &&
      !decl.declared

    // no lots at all for the given period
    const isIdle = !Object.values(decl.lots).some((v) => v === 0)

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
          decl.checked && styles.declarationChecked,
          !decl.checked && decl.declared && styles.declarationDeclared,
          isInProgress && styles.declarationInProgress,
          isIdle && styles.declarationIdle
        )}
      >
        <ul className={styles.declarationSummary}>
          <li>{v.declarations[month]?.lots.drafts ?? 0} brouillons</li>
          <li>{v.declarations[month]?.lots.validated ?? 0} envoyés</li>
          <li>{v.declarations[month]?.lots.received ?? 0} reçus</li>
          <li>{v.declarations[month]?.lots.corrections ?? 0} corrections</li>
        </ul>

        {!decl.declared && (
          <Bell
            className={styles.declarationValidation}
            title="Relancer l'utilisateur"
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              sendReminder(decl)
            }}
          />
        )}

        {!decl.checked && decl.declared && (
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

        {decl.checked && (
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

const Declarations = () => {
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
        declaration.month,
        declaration.year
      )
    }
  }

  useEffect(() => {
    getDeclarations()
  }, [getDeclarations])

  const [entities = [], months = [], declarationsByEntites = {}] =
    declarations.data ?? []

  const columns = months?.map((month) => ({
    header: month,
    render: renderMonthSummary(month, askDeclarationCheck, askSendReminder),
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
