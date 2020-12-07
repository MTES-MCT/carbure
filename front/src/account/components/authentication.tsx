import { SettingsGetter } from "settings/hooks/use-get-settings"

import { Button, LabelInput, Title } from "common/system"
import { Edit } from "common/system/icons"
import { Section, SectionBody, SectionHeader } from "common/system/section"

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
        <Button level="primary" icon={Edit}>
          Modifier mes identifiants
        </Button>
      </SectionHeader>

      <SectionBody>
        <LabelInput
          readOnly
          label="Addresse email"
          defaultValue={settings.data?.email}
        />
      </SectionBody>
    </Section>
  )
}
