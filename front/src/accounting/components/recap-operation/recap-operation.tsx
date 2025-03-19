import { Balance } from "accounting/types"
import { OperationText } from "../operation-text"
import { formatSector } from "accounting/utils/formatters"
import { useTranslation } from "react-i18next"
import { useUnit } from "common/hooks/unit"
import { Grid } from "common/components/scaffold"
import { ExtendedUnit, Unit } from "common/types"

type RecapOperationProps = {
  balance: Balance
  unit?: Unit | ExtendedUnit
}

export const RecapOperation = ({
  balance,
  unit: customUnit,
}: RecapOperationProps) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit(customUnit)

  return (
    <>
      <OperationText
        title={t("Filière")}
        description={formatSector(balance.sector)}
      />
      <OperationText
        title={t("Catégorie")}
        description={balance.customs_category ?? ""}
      />
      <OperationText
        title={t("Biocarburant")}
        description={balance.biofuel ? balance.biofuel.code : ""}
      />
      <OperationText
        title={t("Solde disponible {{biofuel}}", {
          biofuel: balance.biofuel?.code,
        })}
        description={
          balance.available_balance
            ? formatUnit(balance.available_balance, { fractionDigits: 0 })
            : ""
        }
      />
    </>
  )
}

export const RecapOperationGrid = ({
  children,
}: {
  children: React.ReactNode
}) => {
  return (
    <Grid style={{ gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: "24px" }}>
      {children}
    </Grid>
  )
}
