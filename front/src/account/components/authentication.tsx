import { SettingsGetter } from "settings/hooks/use-get-settings"

import { Title } from "common/components"
import { LabelInput } from "common/components/input"
import { Button } from "common/components/button"
import { Edit } from "common/components/icons"
import { Section, SectionBody, SectionHeader } from "common/components/section"

type AccountAuthenticationProps = {
  settings: SettingsGetter
}

export const AccountAuthentication = ({
  settings,
}: AccountAuthenticationProps) => {
  return (
    <Section>
      <SectionHeader>
        <Title>Identifiants</Title>
        <Button disabled level="primary" icon={Edit}>
          Modifier mes identifiants
        </Button>
      </SectionHeader>

      <SectionBody>
        <LabelInput
          readOnly
          label="Addresse email"
          value={settings.data?.email ?? ""}
        />
      </SectionBody>
    </Section>
  )
}
