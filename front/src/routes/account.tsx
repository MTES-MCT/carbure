import { SettingsGetter } from "../hooks/helpers/use-get-settings"

import { Main, Title } from "../components/system"
import { SettingsHeader, SettingsBody } from "../components/settings"

import {
  AccountAccesRights,
  AccountAuthentication,
} from "../components/account"

type AccountProps = {
  settings: SettingsGetter
}

const Account = ({ settings }: AccountProps) => {
  return (
    <Main>
      <SettingsHeader>
        <Title>Mon compte</Title>
      </SettingsHeader>

      <SettingsBody>
        <AccountAccesRights settings={settings} />
        <AccountAuthentication settings={settings} />
      </SettingsBody>
    </Main>
  )
}
export default Account
