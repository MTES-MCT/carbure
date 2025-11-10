import { SectorTabs } from "accounting/types"
import { lazy, useEffect } from "react"
import { useNavigate, useParams } from "react-router"
import { usePrivateNavigation } from "common/layouts/navigation"
import { BetaPage } from "common/molecules/beta-page"
import { useTranslation } from "react-i18next"

const BalancesBiofuels = lazy(() => import("./biofuels"))
const BalancesElec = lazy(() => import("./elec"))

const Balances = () => {
  const { category } = useParams()
  const navigate = useNavigate()
  const { t } = useTranslation()
  usePrivateNavigation(<BetaPage title={t("Comptabilité")} />)

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
