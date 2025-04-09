import { SectorTabs } from "accounting/types"
import { lazy, useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"

const BalancesBiofuels = lazy(() => import("./biofuels"))

const Balances = () => {
  const { status } = useParams()
  const navigate = useNavigate()

  useEffect(() => {
    if (status !== SectorTabs.BIOFUELS) {
      navigate(`${SectorTabs.BIOFUELS}`)
    }
  }, [status, navigate])

  return <>{status === "biofuels" && <BalancesBiofuels />}</>
}

export default Balances
