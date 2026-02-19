import { Content, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { useTranslation } from "react-i18next"
import { Outlet } from "react-router-dom"

export const TeneurLayout = () => {
  const { t } = useTranslation()

  return (
    <>
      <Row style={{ columnGap: "40px", alignItems: "flex-end" }}>
        <div>
          <Select
            options={[{ label: `${t("Année")} 2025`, value: 2025 }]}
            value={2025}
            disabled
          />
        </div>
      </Row>
      <Content marginTop>
        <Outlet />
      </Content>
    </>
  )
}
