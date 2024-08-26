import { DepotType } from "carbure/types"
import { useMemo } from "react"

export const useDeliverySiteFlags = (depotType?: DepotType) =>
  useMemo(
    () => ({
      isPowerPlant: depotType === DepotType.PowerPlant,
      isHeatPlant: depotType === DepotType.HeatPlant,
      isCogenerationPlant: depotType === DepotType.CogenerationPlant,
    }),
    [depotType]
  )
