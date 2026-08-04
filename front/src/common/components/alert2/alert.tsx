import {
  Alert as AlertDSFR,
  type AlertProps as AlertDSFRProps,
} from "@codegouvfr/react-dsfr/Alert"
import cl from "clsx"
import css from "./alert.module.css"

export const Alert = (props: AlertDSFRProps) => {
  return <AlertDSFR {...props} className={cl(css.alert, props.className)} />
}
