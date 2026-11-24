import { IcpeRegimeEnum } from "api-schema"
import { RadioGroup, RadioGroupProps } from "common/components/inputs2"
import { useTranslation } from "react-i18next"

export const IcpeRegimeField = ({
  label,
  ...props
}: Omit<RadioGroupProps<IcpeRegimeEnum | null>, "options">) => {
  const { t } = useTranslation()

  return (
    <RadioGroup
      {...props}
      label={label ?? t("Régime ICPE")}
      options={[
        {
          value: IcpeRegimeEnum.AUTHORIZATION,
          label: t("Autorisation"),
        },
        {
          value: IcpeRegimeEnum.REGISTRATION,
          label: t("Enregistrement"),
        },
        {
          value: IcpeRegimeEnum.DECLARATION_PERIODIC_CONTROLS,
          label: t("Déclaration (avec contrôles périodiques)"),
        },
      ]}
    />
  )
}
