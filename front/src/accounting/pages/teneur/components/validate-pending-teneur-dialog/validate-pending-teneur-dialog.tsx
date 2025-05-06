import { Dialog } from "common/components/dialog2"
import { useTranslation } from "react-i18next"
import { validateTeneur } from "../../api"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"

import { Button } from "common/components/button2"
import { useNotify } from "common/components/notifications"
import { Tabs } from "common/components/tabs2"
import { GasStationFill } from "common/components/icon"
import { BiofuelsTab } from "./biofuels-tab"
import { useState } from "react"

export const ValidatePendingTeneurDialog = ({
  onClose,
}: {
  onClose: () => void
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const [tab, setTab] = useState("biofuels")

  const mutation = useMutation(validateTeneur, {
    onSuccess: () => {
      onClose()
      notify(
        t("Les opérations de teneur en attente ont été validées avec succès."),
        { variant: "success" }
      )
    },
    onError: () => {
      notify(
        t(
          "Une erreur est survenue lors de la validation des opérations de teneur en attente."
        ),
        { variant: "danger" }
      )
    },
  })

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Valider ma teneur")}</Dialog.Title>}
      footer={
        <Button
          onClick={() => mutation.execute(entity.id)}
          loading={mutation.loading}
        >
          {t("Valider ma teneur")}
        </Button>
      }
      fullWidth
    >
      <Tabs
        tabs={[
          {
            key: "biofuels",
            label: t("Biocarburants"),
            icon: GasStationFill,
          },
        ]}
        focus={tab}
        onFocus={setTab}
      />
      <BiofuelsTab />
    </Dialog>
  )
}
