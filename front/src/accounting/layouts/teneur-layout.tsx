import { useAnnualDeclarationTiruertYears } from "accounting/hooks/use-annual-declaration-tiruert-years"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { Content, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { Outlet } from "react-router-dom"

export const TeneurLayout = () => {
  const { selectedYear } = useAnnualDeclarationTiruert()
  const years = useAnnualDeclarationTiruertYears()

  return (
    <>
      <Row style={{ columnGap: "40px", alignItems: "flex-end" }}>
        <div>
          <Select
            options={years.options}
            value={selectedYear}
            onChange={years.setYear}
          />
        </div>
      </Row>
      <Content marginTop>
        <Outlet />
      </Content>
    </>
  )
}
