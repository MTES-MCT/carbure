import { Content } from "common/components/scaffold"
import { Outlet, useParams } from "react-router-dom"
import { AccountingSectorTabs } from "accounting/components/accounting-sector-tabs"

const OperationsBalancesLayout = () => {
  // extract current TIRUERT section: "balances" or "operations"
  const params = useParams()
  const [sector] = (params["*"] ?? "").split("/")
  return (
    <>
      <AccountingSectorTabs pathPrefix={sector} />

      <Content>
        <Outlet />
      </Content>
    </>
  )
}

export default OperationsBalancesLayout
