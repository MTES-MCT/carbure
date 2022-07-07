import { Trans, useTranslation } from "react-i18next"
import { useUser } from "carbure/hooks/user"
import { TextInput } from "common/components/input"
import { Button } from "common/components/button"
import { Edit } from "common/components/icons"
import { Panel } from "common/components/scaffold"

export const AccountAuthentication = () => {
  const { t } = useTranslation()
  const user = useUser()

  return (
    <Panel>
      <header>
        <h1>
          <Trans>Identifiants</Trans>
        </h1>
        <Button
          asideX
          disabled
          variant="primary"
          icon={Edit}
          label={t("Modifier mes identifiants")}
        />
      </header>

      <footer>
        <TextInput
          readOnly
          label={t("Addresse email")}
          value={user.email}
          style={{ flex: 1 }}
        />
      </footer>
    </Panel>
  )
}
