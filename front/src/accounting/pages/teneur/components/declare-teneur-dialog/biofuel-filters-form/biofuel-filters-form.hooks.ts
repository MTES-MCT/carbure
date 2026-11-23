import { useMemo } from "react"

import { Balance, OperationSector } from "accounting/types"

export const useCompatibleSectors = (balance?: Balance) => {
  return useMemo(() => {
    const biofuel = balance?.biofuel
    if (!biofuel) return []

    return [
      biofuel.compatible_essence && OperationSector.ESSENCE,
      biofuel.compatible_diesel && OperationSector.GAZOLE,
      biofuel.compatible_gpl && OperationSector.GPL,
      biofuel.compatible_maritime && OperationSector.MARITIME,
      balance.sector,
    ].filter(
      (sector, index, sectors): sector is OperationSector =>
        Boolean(sector) && sectors.indexOf(sector) === index
    )
  }, [balance])
}
