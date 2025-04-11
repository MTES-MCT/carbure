import { SectorTabs } from "accounting/types"
import { lazy, useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"

const OperationsBiofuels = lazy(() => import("./biofuels"))
const OperationsElec = lazy(() => import("./elec"))

const Operations = () => {
  const { category } = useParams()
  const navigate = useNavigate()

  useEffect(() => {
    if (!category) navigate(`${SectorTabs.BIOFUELS}`)
  }, [category, navigate])

  return (
    <>
      {category === "biofuels" && <OperationsBiofuels />}
      {category === "elec" && <OperationsElec />}
    </>
  )
}

export default Operations
