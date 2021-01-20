import { Main, Title } from "common/components"
import { SettingsBody, SettingsHeader } from "settings/components/common"

const Dashboard = () => {
  return (
    <Main>
      <SettingsHeader>
        <Title>Tableau de bord</Title>
      </SettingsHeader>

      <SettingsBody></SettingsBody>
    </Main>
  )
}

export default Dashboard
