import { SettingsGetter } from "settings/hooks/use-get-settings"

import { Main, Title } from "common/components"
import { SettingsHeader, SettingsBody } from "settings/components/common"

import { prompt } from "common/components/dialog"
import { AccountAccesRights, EntityPrompt } from "./components/access-rights"
import { AccountAuthentication } from "./components/authentication"
import useAPI from "common/hooks/use-api"
import * as api from "./api"

export interface AccountHook {
  isLoading: boolean
  askEntityAccess: () => void
}

function useAccount(settings: SettingsGetter): AccountHook {
  const [requestAccess, resolveAccess] = useAPI(api.requestAccess)

  const isLoading = settings.loading || requestAccess.loading

  async function askEntityAccess() {
    const entity = await prompt(
      "Ajout organisation",
      "Recherchez la société qui vous emploie pour pouvoir accéder à ses données.",
      EntityPrompt
    )

    if (entity) {
      await resolveAccess(entity.id, "")
      settings.resolve()
    }
  }

  return {
    isLoading,
    askEntityAccess,
  }
}

type AccountProps = {
  settings: SettingsGetter
}

const Account = ({ settings }: AccountProps) => {
  const account = useAccount(settings)

  return (
    <Main>
      <SettingsHeader>
        <Title>Mon compte</Title>
      </SettingsHeader>

      <SettingsBody>
        <AccountAccesRights settings={settings} account={account} />
        <AccountAuthentication settings={settings} />
      </SettingsBody>
    </Main>
  )
}

export default Account
