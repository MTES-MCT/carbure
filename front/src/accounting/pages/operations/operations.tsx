import { SectorTabs } from "accounting/types"
import { lazy, useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"

const OperationsBiofuels = lazy(() => import("./biofuels"))
const OperationsElec = lazy(() => import("./elec"))

const Operations = () => {
  const { status } = useParams()
  const navigate = useNavigate()

  useEffect(() => {
    if (!status) navigate(`${SectorTabs.BIOFUELS}`)
  }, [status, navigate])

  return (
    <>
      {status === "biofuels" && <OperationsBiofuels />}
      {status === "elec" && <OperationsElec />}
    </>
  )
}

export default Operations
