import { useTranslation } from "react-i18next"
import { Lot, LotQuery } from "transactions-v2/types"
import Menu from "common-v2/components/menu"
import { Check } from "common-v2/components/icons"

export interface AcceptManyButtonProps {
  disabled?: boolean
  query: LotQuery
  selection: number[]
}

export const AcceptManyButton = ({
  disabled,
  query,
  selection,
}: AcceptManyButtonProps) => {
  const { t } = useTranslation()

  return (
    <Menu
      disabled={disabled}
      variant="success"
      icon={Check}
      label={
        selection.length > 0 ? t("Accepter la sélection") : t("Accepter tout")
      }
      items={[
        { label: t("Incorporation") },
        { label: t("Mise à consommation") },
        { label: t("Livraison directe") },
      ]}
    />
  )
}

export interface AcceptOneButtonProps {
  icon?: boolean
  lot: Lot
}

export const AcceptOneButton = ({ icon, lot }: AcceptOneButtonProps) => {
  const { t } = useTranslation()

  return (
    <Menu
      captive
      variant={icon ? "icon" : "success"}
      icon={Check}
      label={t("Accepter le lot")}
      items={[
        { label: t("Incorporation") },
        { label: t("Mise à consommation") },
        { label: t("Livraison directe") },
      ]}
    />
  )
}
