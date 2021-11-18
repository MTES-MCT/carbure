import { useTranslation } from "react-i18next"
import { usePortal } from "common-v2/components/portal"
import Menu from "common-v2/components/menu"
import Dialog from "common-v2/components/dialog"
import Button from "common-v2/components/button"
import { Check } from "common-v2/components/icons"
import { LotQuery } from "../hooks/lot-query"

export interface AcceptButtonProps {
  disabled?: boolean
  query: LotQuery
  selection: number[]
}

export const AcceptButton = ({
  disabled,
  query,
  selection,
}: AcceptButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

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
        {
          label: t("Livraison directe"),
          action: () =>
            portal((close) => (
              <Dialog onClose={close}>
                <header>
                  <h1>Livraison directe</h1>
                </header>
                <main>
                  <section>Description</section>
                </main>
                <footer>
                  <Button asideX label="Annuler" action={close} />
                </footer>
              </Dialog>
            )),
        },
      ]}
    />
  )
}
