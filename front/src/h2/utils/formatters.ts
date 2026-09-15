import { AccessType } from "h2/types"
import i18next from "i18next"

export const formatAccessType = (accessType: AccessType) => {
  switch (accessType) {
    case AccessType.PRIVATE:
      return i18next.t("Privé")
    case AccessType.PUBLIC:
      return i18next.t("Public")
  }
}
