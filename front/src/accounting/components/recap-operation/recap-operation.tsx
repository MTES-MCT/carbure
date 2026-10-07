import { Balance } from "accounting/types"
import { OperationText } from "../operation-text"
import { formatSector } from "accounting/utils/formatters"
import { useTranslation } from "react-i18next"
import { Grid } from "common/components/scaffold"
import { ExtendedUnit } from "common/types"
import { formatNumber } from "common/utils/formatters"

type RecapOperationProps = {
  balance: Balance
  sector?: string
  unit?: ExtendedUnit
}

export const RecapOperation = ({ balance, sector }: RecapOperationProps) => {
  const { t } = useTranslation()

  return (
    <>
      <OperationText
        title={t("Filière")}
        description={formatSector(sector ?? balance.sector)}
      />
      <OperationText
        title={t("Catégorie")}
        description={balance.customs_category ?? ""}
      />
      <OperationText
        title={t("Biocarburant")}
        description={balance.biofuel ? balance.biofuel.code : ""}
      />
      {balance.biofuel && (
        <OperationText
          title={t("PCI")}
          description={`${formatNumber(balance.biofuel.pci_litre)} MJ/L`}
        />
      )}
      {balance.biofuel && balance.biofuel.renewable_energy_share !== 1 && (
        <OperationText
          title={t("Taux renouvelable")}
          description={`${formatNumber(balance.biofuel.renewable_energy_share * 100)} %`}
        />
      )}
    </>
  )
}

export const RecapOperationGrid = ({
  children,
}: {
  children: React.ReactNode
}) => {
  return (
    <Grid style={{ gridTemplateColumns: "1fr 1fr 1fr 1fr 1fr", gap: "24px" }}>
      {children}
    </Grid>
  )
}
