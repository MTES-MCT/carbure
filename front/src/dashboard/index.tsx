import useAPI from "common/hooks/use-api"
import { Main, Title } from "common/components"
import { SettingsBody, SettingsHeader } from "settings/components/common"

import * as api from "./api"
import { useEffect } from "react"
import Declarations from "./components/declarations"

const Dashboard = () => {
  const [declarations, getDeclarations] = useAPI(api.getDeclarations)

  useEffect(() => {
    getDeclarations()
  }, [getDeclarations])

  return (
    <Main>
      <SettingsHeader>
        <Title>Tableau de bord</Title>
      </SettingsHeader>

      <SettingsBody>
        <Declarations declarations={declarations} />
      </SettingsBody>
    </Main>
  )
}

export default Dashboard
