import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Text } from "common/components/text"
import { useState } from "react"
import { useTranslation } from "react-i18next"

export const ApplicationDownDialog = () => {
  const { t } = useTranslation()
  const [open, setOpen] = useState(true)

  if (!open) return null

  return (
    <Portal>
      <Dialog
        onClose={() => setOpen(false)}
        fullWidth
        header={<Dialog.Title>{t("Application indisponible")}</Dialog.Title>}
      >
        <Text>
          {t("L'application est actuellement indisponible.")} <br />
          <br />
          {t("Veuillez réessayer plus tard.")}
        </Text>
      </Dialog>
    </Portal>
  )
}
