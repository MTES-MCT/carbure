import { Balance, ElecBalance } from "accounting/types"
import { formatSector } from "accounting/utils/formatters"
import { Column, Cell } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { SectorObjective } from "../../types"
import {
  formatObjectiveGJ,
  formatObjectiveGJFromMj,
} from "../../utils/objectives"
import { energyFromLiters } from "../../utils/liters"

const formatElecBalanceGj = (valueMj: number) =>
  formatObjectiveGJFromMj(valueMj)

const formatBiofuelBalanceGj = (liters: number, pciLitre?: number) => {
  if (!pciLitre) return "-"

  return formatObjectiveGJ(energyFromLiters(liters, pciLitre).gj)
}

export const useBiofuelTeneurColumns = () => {
  const { t } = useTranslation()
  const columns: Column<Balance>[] = [
    {
      header: t("Biocarburant"),
      cell: (item) => item.biofuel?.code,
    },
    {
      header: t("Catégorie"),
      cell: (item) => item.customs_category,
    },
    {
      header: `${t("Solde initial")} (GJ)`,
      cell: (item) => (
        <Cell
          text={formatBiofuelBalanceGj(
            item.available_balance + item.pending_teneur,
            item.biofuel?.pci_litre
          )}
        />
      ),
    },
    {
      header: `${t("Teneur à valider")} (GJ)`,
      cell: (item) => (
        <Cell
          text={formatBiofuelBalanceGj(
            item.pending_teneur,
            item.biofuel?.pci_litre
          )}
        />
      ),
    },
    {
      header: `${t("Solde final")} (GJ)`,
      cell: (item) => (
        <Cell
          text={formatBiofuelBalanceGj(
            item.available_balance,
            item.biofuel?.pci_litre
          )}
        />
      ),
    },
  ]

  return columns
}

export const useBiofuelTeneurSectorColumns = () => {
  const { t } = useTranslation()
  const columns: Column<SectorObjective>[] = [
    {
      header: t("Filière"),
      cell: (item) => <Cell text={formatSector(item.code)} />,
    },
    {
      header: `${t("Avancement initial")} (GJ)`,
      cell: (item) => (
        <Cell text={formatObjectiveGJ(item.progress.teneur_declared)} />
      ),
    },
    {
      header: `${t("Teneur à valider")} (GJ)`,
      cell: (item) => (
        <Cell text={formatObjectiveGJ(item.progress.pending_teneur)} />
      ),
    },
    {
      header: `${t("Avancement final")} (GJ)`,
      cell: (item) => (
        <Cell text={formatObjectiveGJ(item.progress.total_teneur_declared)} />
      ),
    },
  ]

  return columns
}

export const useElecTeneurColumns = () => {
  const { t } = useTranslation()
  const columns: Column<ElecBalance>[] = [
    {
      header: t("Filière"),
      cell: (item) => <Cell text={formatSector(item.sector)} />,
    },
    {
      header: `${t("Solde initial")} (GJ)`,
      cell: (item) => (
        <Cell
          text={formatElecBalanceGj(
            item.available_balance + item.pending_teneur
          )}
        />
      ),
    },
    {
      header: `${t("Teneur à valider")} (GJ)`,
      cell: (item) => <Cell text={formatElecBalanceGj(item.pending_teneur)} />,
    },
    {
      header: `${t("Solde final")} (GJ)`,
      cell: (item) => (
        <Cell text={formatElecBalanceGj(item.available_balance)} />
      ),
    },
  ]

  return columns
}
