import { useAdmin } from "./hooks/useAdmin"
import { useSaf } from "./hooks/useSaf"
import { useChargePoints } from "./hooks/useChargePoints"
import { useElec } from "./hooks/useElec"
import { useBiofuels } from "./hooks/useBiofuels"
import { useDoubleCount } from "./hooks/useDoubleCount"

export const usePrivateSidebar = () => {
  const biofuels = useBiofuels()

  const elec = useElec()
  const chargePoints = useChargePoints()
  const saf = useSaf()
  const admin = useAdmin()
  const doubleCount = useDoubleCount()

  return [admin, ...biofuels, doubleCount, ...elec, ...chargePoints, saf]
    .filter(
      (category) =>
        category.condition === undefined || category.condition === true
    )
    .map((category) => ({
      ...category,
      children: category.children.filter(
        (child) => child.condition === undefined || child.condition === true
      ),
    }))
}
