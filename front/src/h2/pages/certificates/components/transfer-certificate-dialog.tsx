import { useTranslation } from "react-i18next"

import { Dialog } from "common/components/dialog2"
import { NavLink } from "common/components/nav-link"
import { useRoutes } from "common/hooks/routes"
import { Action } from "traceability/types"

export type TransferCertificateDialogProps = {
  action: Action
  onClose: () => void
}

const CURRENT_YEAR = new Date().getFullYear()

export const TransferCertificateDialog = ({
  action,
  onClose,
}: TransferCertificateDialogProps) => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const parent = action.parent
  const year = parent?.working_date
    ? new Date(parent.working_date).getFullYear()
    : CURRENT_YEAR
  const lotPath = parent ? routes.HYDROGEN(year).LOT(parent.id) : undefined

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Certificat de cession")}</Dialog.Title>}
    >
      {parent && lotPath && (
        <NavLink to={lotPath} underline>
          {t("Certificat lié au lot n°{{id}}", { id: parent.id })}
        </NavLink>
      )}
    </Dialog>
  )
}
