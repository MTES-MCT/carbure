import { matchPath, useLocation, useResolvedPath } from "react-router-dom"
import { useRef } from "react"
import { SectorTabs } from "accounting/types"

// Helps when switching from tiruert balances and operations
// by making sure we stay on the same tab on the two pages.
// For example, if you were on the ELEC tabs of balances/
// and switched to operations/, you'd automatically go to operations/elec
export function useLastSectorVisited() {
  const location = useLocation()
  const lastSector = useRef<string>(SectorTabs.BIOFUELS)

  const pattern = useResolvedPath(":category/:sector")
  const match = matchPath(pattern.pathname, location.pathname)

  if (match?.params.sector) {
    lastSector.current = match?.params.sector
  }

  return lastSector.current
}
