import { Button } from "common/components/button2"
import { SearchInput } from "common/components/inputs2"
import { ActionBar, Content, Main, Row } from "common/components/scaffold"
import { Select } from "common/components/selects2"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useTranslation } from "react-i18next"

export const SupplyPlan = () => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Mes plans d'approvisionnement"))
  return (
    <Main>
      <Row>
        <Select options={[]} value={2025} onChange={() => {}} />
        <Button onClick={() => {}} iconId="ri-upload-line" asideX>
          {t("Valider mes informations annuelles")}
        </Button>
      </Row>
      <Content marginTop>
        <ActionBar>
          <ActionBar.Grow>
            <SearchInput />
          </ActionBar.Grow>
          <Button
            onClick={() => {}}
            iconId="ri-add-line"
            asideX
            priority="secondary"
          >
            {t("Ajouter un intrant")}
          </Button>
        </ActionBar>
      </Content>
    </Main>
  )
}
