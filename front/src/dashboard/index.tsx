import { Main, Title } from "common/components"
import { SettingsBody, SettingsHeader } from "settings/components/common"

import Declarations from "./components/declarations"

const Dashboard = () => {
  return (
    <Main>
      <SettingsHeader>
        <Title>Tableau de bord</Title>
      </SettingsHeader>

      <SettingsBody>
        <Declarations />
      </SettingsBody>
    </Main>
  )
}

export default Dashboard
