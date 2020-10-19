import React from "react"
import { AppHook } from "../hooks/use-app"

import { Main, Box, Title } from "../components/system"
import { Redirect } from "../components/relative-route"
import { EntitySelection } from "../hooks/helpers/use-entity"

type SettingsProps = {
  entity: EntitySelection
}

const Settings = ({ entity }: SettingsProps) => {
  return (
    <Main>
	  <Box>
	    <div>
	      <div>
	        <Title>Settings</Title>
	      </div>
	    </div>
	  </Box>
    </Main>
  )
}
export default Settings
