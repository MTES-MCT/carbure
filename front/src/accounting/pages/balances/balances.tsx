import { SectorTabs } from "accounting/types"
import { lazy, useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"

const BalancesBiofuels = lazy(() => import("./biofuels"))
const BalancesElec = lazy(() => import("./elec"))

const Balances = () => {
  const { category } = useParams()
  const navigate = useNavigate()

  useEffect(() => {
    if (!category) navigate(`${SectorTabs.BIOFUELS}`)
  }, [category, navigate])

  return (
    <>
      {category === "biofuels" && <BalancesBiofuels />}
      {category === "elec" && <BalancesElec />}
    </>
  )
}

export default Balances
