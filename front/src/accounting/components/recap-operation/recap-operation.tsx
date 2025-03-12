import { Balance } from "accounting/types"
import { OperationText } from "../operation-text"
import { Grid } from "common/components/scaffold"
import { formatSector } from "accounting/utils/formatters"
import { useTranslation } from "react-i18next"
import { useUnit } from "common/hooks/unit"

type RecapOperationProps = {
  balance: Balance
}

export const RecapOperation = ({ balance }: RecapOperationProps) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit()

  return (
    <Grid>
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
            ? formatUnit(balance.available_balance, 0)
            : ""
        }
      />
    </Grid>
  )
}
