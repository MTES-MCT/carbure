import { Fragment, useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import cl from "clsx"

import { Declaration, Entity, EntityType } from "common/types"
import { Box, LoaderOverlay, Title } from "common/components"
import Table, { Row, padding } from "common/components/table"
import { Section, SectionHeader } from "common/components/section"
import styles from "./declarations.module.css"
import useAPI from "common/hooks/use-api"
import {
  AlertCircle,
  Bell,
  Check,
  ChevronLeft,
  ChevronRight,
  Cross,
} from "common/components/icons"
import { confirm } from "common/components/dialog"
import { Button } from "common/components/button"
import usePeriod, {
  prettyPeriod,
  PeriodHook,
  stdPeriod,
} from "common/hooks/use-period"
import { Alert, AlertLink } from "common/components/alert"
import * as api from "../api"
import { DeclarationsByEntities, DeclarationsByMonth } from "../helpers"

type RowData = { entity: Entity; declarations: DeclarationsByMonth }

const entityColumn = {
  className: styles.declarationEntity,
  render: (v: RowData) => v.entity.name,
}

function renderMonthHeader(
  month: string,
  period: PeriodHook,
  index: number,
  total: number
) {
  const isFirst = index === 0
  const isLast = index === total - 1

  return (
    <Fragment>
      {isFirst && (
        <Button
          icon={ChevronLeft}
          onClick={period.prev}
          className={styles.declarationPeriodPrev}
        />
      )}
      <span>{month}</span>
      {isLast && (
        <Button
          icon={ChevronRight}
          onClick={period.next}
          className={styles.declarationPeriodNext}
        />
      )}
    </Fragment>
  )
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
    const navigate = useNavigate()

    const decl = v.declarations[month]

    if (!decl) return "N/A"

    const { drafts = 0, output = 0, input = 0, corrections = 0 } = decl.lots
    const ev = evaluateDeclaration(decl)

    const pushToTransactions = () => {
      const queryParams = new URLSearchParams()

      queryParams.append("periods", stdPeriod(decl))

      if (v.entity.entity_type === EntityType.Operator) {
        queryParams.append("clients", v.entity.name)
      } else {
        queryParams.append("vendors", v.entity.name)
      }

      navigate(`../transactions/declaration?${queryParams}`)
    }

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
        <div className={styles.declarationSummary}>
          <span>
            {drafts === 0
              ? "-"
              : drafts === 1
              ? "1 brouillon"
              : `${drafts} brouillons`}
          </span>

          <span>
            {output === 0
              ? "-"
              : output === 1
              ? "1 envoyé"
              : `${output} envoyés`}
          </span>

          <span>
            {input === 0 ? "-" : input === 1 ? "1 reçu" : `${input} reçus`}
          </span>

          <span>
            {corrections === 0
              ? "-"
              : corrections === 1
              ? "1 correction"
              : `${corrections} corrections`}
          </span>
        </div>

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
  declarations: DeclarationsByEntities
  months: string[]
  entities: Entity[]
  period: PeriodHook
  onCheck: (d: Declaration, t: boolean) => Promise<any>
  onRemind: (d: Declaration) => Promise<any>
}

const DeclarationTable = ({
  declarations,
  months,
  entities,
  period,
  onCheck,
  onRemind,
}: DeclarationTableProps) => {
  const columns = months?.map((month, i) => ({
    header: renderMonthHeader(month, period, i, months.length),
    className: styles.declarationPeriod,
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
    .sort((a, b) =>
      a.value.entity.name.localeCompare(b.value.entity.name, "fr")
    )

  if (rows.length === 0) {
    return (
      <Alert
        level="warning"
        icon={AlertCircle}
        className={styles.declarationEmpty}
      >
        <span>
          Aucun résultat autour de la période <b>{prettyPeriod(period)}</b>
        </span>
        <AlertLink onClick={period.reset} className={styles.declarationReset}>
          Retourner à la période actuelle
        </AlertLink>
      </Alert>
    )
  }

  return (
    <Table
      className={styles.declarationTable}
      columns={[padding, entityColumn, ...columns]}
      rows={rows}
    />
  )
}

const Declarations = () => {
  const [declarations, getDeclarations] = useAPI(api.getDeclarations)
  const [, checkDeclaration] = useAPI(api.checkDeclaration)
  const [, uncheckDeclaration] = useAPI(api.uncheckDeclaration)
  const [, sendReminder] = useAPI(api.sendDeclarationReminder)

  const [focus, setFocus] = useState(EntityType.Producer)
  const period = usePeriod()

  const [entities = [], months = [], byEntityType = {}] =
    declarations.data ?? []

  async function confirmDeclarationCheck(declaration: Declaration) {
    const ok = await confirm(
      "Validation déclaration",
      "Voulez-vous valider cette déclaration ?"
    )

    if (ok) {
      await checkDeclaration(declaration.id)
      await getDeclarations(period.year, period.month)
    }
  }

  async function cancelDeclarationCheck(declaration: Declaration) {
    const ok = await confirm(
      "Annulation déclaration",
      "Voulez-vous annuler la validation de cette déclaration ?"
    )

    if (ok) {
      await uncheckDeclaration(declaration.id)
      await getDeclarations(period.year, period.month)
    }
  }

  async function askDeclarationCheck(
    declaration: Declaration,
    toggle: boolean
  ) {
    if (toggle) {
      await confirmDeclarationCheck(declaration)
    } else {
      await cancelDeclarationCheck(declaration)
    }
  }

  async function askSendReminder(declaration: Declaration) {
    const ok = await confirm(
      "Relance déclaration",
      `Voulez-vous relancer ${declaration.entity.name} pour la période du ${prettyPeriod(period)} ?` // prettier-ignore
    )

    if (ok) {
      await sendReminder(
        declaration.entity.id,
        declaration.year,
        declaration.month
      )

      await getDeclarations(period.year, period.month)
    }
  }

  useEffect(() => {
    getDeclarations(period.year, period.month)
  }, [getDeclarations, period.year, period.month])

  return (
    <Section>
      <SectionHeader>
        <Title>Résumé des déclarations</Title>

        <Box row className={styles.declarationLegend}>
          <span className={styles.declarationColorCode}>
            <i
              className={cl(
                styles.declarationColor,
                styles.declarationColorInProgress
              )}
            />
            En cours
          </span>

          <span className={styles.declarationColorCode}>
            <i
              className={cl(
                styles.declarationColor,
                styles.declarationColorReminded
              )}
            />
            Relancé
          </span>

          <span className={styles.declarationColorCode}>
            <i
              className={cl(
                styles.declarationColor,
                styles.declarationColorDeclared
              )}
            />
            Déclaré par l'entité
          </span>

          <span className={styles.declarationColorCode}>
            <i
              className={cl(
                styles.declarationColor,
                styles.declarationColorChecked
              )}
            />
            Approuvé par l'administration
          </span>
        </Box>
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

      {declarations.error && (
        <Alert
          level="error"
          icon={AlertCircle}
          className={styles.declarationEmpty}
        >
          {declarations.error}
        </Alert>
      )}

      {focus === EntityType.Producer && (
        <DeclarationTable
          entities={entities}
          months={months}
          period={period}
          declarations={byEntityType[EntityType.Producer]}
          onCheck={askDeclarationCheck}
          onRemind={askSendReminder}
        />
      )}

      {focus === EntityType.Trader && (
        <DeclarationTable
          entities={entities}
          months={months}
          period={period}
          declarations={byEntityType[EntityType.Trader]}
          onCheck={askDeclarationCheck}
          onRemind={askSendReminder}
        />
      )}

      {focus === EntityType.Operator && (
        <DeclarationTable
          entities={entities}
          months={months}
          period={period}
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
