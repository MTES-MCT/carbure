import React from "react"
import { AppHook } from "../hooks/use-app"

import { Main, Box, Title } from "../components/system"
import { Redirect } from "../components/relative-route"
import useEntity from "../hooks/helpers/use-entity"

type MainProps = {
  app: AppHook
}

const Settings = ({ app }: MainProps) => {
  const entity = useEntity()

  if (!app.hasEntity(entity!)) {
    return <Redirect to="/" />
  }

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
