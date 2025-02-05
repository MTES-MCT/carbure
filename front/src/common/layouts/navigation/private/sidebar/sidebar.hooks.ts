import { useAdmin } from "./hooks/useAdmin"
import { useSaf } from "./hooks/useSaf"
import { useChargePoints } from "./hooks/useChargePoints"
import { useElec } from "./hooks/useElec"
import { useBiofuels } from "./hooks/useBiofuels"
import { useDoubleCount } from "./hooks/useDoubleCount"
import { useQuery } from "common/hooks/async"
import useEntity from "carbure/hooks/entity"
import { getNavStats } from "./api"
import { useEffect } from "react"

export const usePrivateSidebar = () => {
  const entity = useEntity()
  const { result, execute } = useQuery(() => getNavStats(entity.id), {
    key: `nav-stats-${entity.id}`,
    params: [],
    executeOnMount: false,
  })

  const biofuels = useBiofuels(result?.data)
  const elec = useElec(result?.data)
  const chargePoints = useChargePoints(result?.data)
  const saf = useSaf(result?.data)
  const admin = useAdmin(result?.data)
  const doubleCount = useDoubleCount(result?.data)

  useEffect(() => {
    if (entity.id !== -1) {
      execute()
    }
  }, [entity.id, execute])

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
