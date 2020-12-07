import { SettingsGetter } from "settings/hooks/use-get-settings"

import { Main, Title } from "common/system"
import { SettingsHeader, SettingsBody } from "settings/components/common"

import { AccountAccesRights } from "./components/access-rights"
import { AccountAuthentication } from "./components/authentication"

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
