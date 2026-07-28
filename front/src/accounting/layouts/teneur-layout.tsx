import { ObjectivesYearSelect } from "accounting/components/objectives-year-select"
import { Content, Row } from "common/components/scaffold"
import { Outlet } from "react-router-dom"

export const TeneurLayout = () => {
  return (
    <>
      <Row style={{ columnGap: "40px", alignItems: "flex-end" }}>
        <div>
          <ObjectivesYearSelect urlRoot="objectives" />
        </div>
      </Row>
      <Content marginTop>
        <Outlet />
      </Content>
    </>
  )
}
