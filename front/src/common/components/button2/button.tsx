import {
  Button as ButtonDSFR,
  ButtonProps as ButtonDSFRProps,
} from "@codegouvfr/react-dsfr/Button"

export type ButtonProps = ButtonDSFRProps

export const Button = (props: ButtonDSFRProps) => {
  return <ButtonDSFR {...props} />
}
