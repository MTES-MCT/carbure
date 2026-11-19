import { useMatch } from "react-router-dom"
import { useRef } from "react"
import { SectorTabs } from "accounting/types"

const sectors: string[] = [SectorTabs.BIOFUELS, SectorTabs.ELEC]

// Helps when switching from tiruert balances and operations
// by making sure we stay on the same tab on the two pages.
// For example, if you were on the ELEC tabs of balances/
// and switched to operations/, you'd automatically go to operations/elec
export function useLastSectorVisited() {
  const lastSector = useRef<string>(SectorTabs.BIOFUELS)

  const match = useMatch("/org/:entity/accounting/:category/:sector")

  if (match?.params.sector && sectors.includes(match.params.sector)) {
    lastSector.current = match?.params.sector
  }

  return lastSector.current
}
