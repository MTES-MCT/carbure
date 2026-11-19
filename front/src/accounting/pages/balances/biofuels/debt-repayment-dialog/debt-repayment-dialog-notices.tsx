import { Debt, DebtType } from "accounting/types"
import { formatAccountingUnit } from "accounting/utils/formatters"
import { Alert } from "common/components/alert2"
import { Box } from "common/components/scaffold"
import { Notice } from "common/components/notice"
import { ExtendedUnit, Unit } from "common/types"
import { formatUnit } from "common/utils/formatters"
import { Trans, useTranslation } from "react-i18next"
import { DebtRepaymentDialogForm } from "./debt-repayment-dialog.types"

export const formatDebtTco2 = (value: number) =>
  formatUnit(value, ExtendedUnit.tCO2ev, {
    fractionDigits: 2,
    mode: "trunc",
  })

type DebtRemainingNoticeProps = {
  debt: Debt
  debtType: DebtType
  simulation: DebtRepaymentDialogForm["simulation"]
}

export const DebtRemainingNotice = ({
  debt,
  debtType,
  simulation,
}: DebtRemainingNoticeProps) => {
  const { t } = useTranslation()

  return (
    <Alert
      severity="info"
      small
      description={
        <p>
          <Trans
            components={{ b: <b /> }}
            t={t}
            values={{
              volume:
                debtType === DebtType.TCO2
                  ? formatDebtTco2(simulation?.debt_tco2 ?? debt.remaining_tco2)
                  : formatAccountingUnit(debt.remaining_volume, Unit.l),
            }}
            defaults="Vous devez <b>{{volume}}</b>"
          />
        </p>
      }
    />
  )
}

export const DebtRepaymentTco2Summary = ({
  simulation,
}: Pick<DebtRepaymentDialogForm, "simulation">) => {
  const { t } = useTranslation()

  if (!simulation) return null

  const values = {
    volume: formatAccountingUnit(simulation.total_volume, Unit.l),
    repaid: formatDebtTco2(simulation.debt_tco2 - simulation.remaining_tco2),
    remaining: formatDebtTco2(simulation.remaining_tco2),
  }

  return (
    <Box>
      {simulation.repaid_tco2 > 0 ? (
        <Notice variant={simulation.remaining_tco2 > 0 ? "warning" : "info"}>
          <div>
            <p>
              <Trans
                t={t}
                components={{ b: <b /> }}
                values={values}
                defaults="Pour acquitter <b>{{repaid}}</b>, avec les lots sélectionnés précédemment, nous allons prélever <b>{{volume}}</b>."
              />
            </p>
            {simulation.remaining_tco2 > 0 && (
              <p>
                <Trans
                  t={t}
                  components={{ b: <b /> }}
                  values={values}
                  defaults="Les lots disponibles ne permettent qu'un remboursement partiel. Il restera <b>{{remaining}}</b> à acquitter."
                />
              </p>
            )}
          </div>
        </Notice>
      ) : (
        <Alert
          severity="warning"
          small
          description={t(
            "Les lots sélectionnés ne permettent pas de rembourser la dette en tCO2 évitées. Modifiez vos filtres."
          )}
        />
      )}
    </Box>
  )
}
