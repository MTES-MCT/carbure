import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useTranslation } from "react-i18next"
import { SupplyInputForm } from "./supply-input-form"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { createSupplyInput } from "../api"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

export const CreateSupplyInputDialog = ({
  onClose,
}: {
  onClose: () => void
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { currentAnnualDeclarationKey, selectedYear } = useAnnualDeclaration()

  const createSupplyInputMutation = useMutation(createSupplyInput, {
    invalidates: ["supply-plan-inputs", currentAnnualDeclarationKey],
    onSuccess: () => {
      notify(t("L'intrant a bien été créé."), {
        variant: "success",
      })
    },
    onError: (e) => {
      notifyError(e)
    },
  })

  return (
    <Dialog
      header={<Dialog.Title>{t("Ajouter un intrant")}</Dialog.Title>}
      footer={
        <Button
          type="submit"
          loading={createSupplyInputMutation.loading}
          nativeButtonProps={{ form: "supply-input-form" }}
        >
          {t("Valider l'intrant")}
        </Button>
      }
      onClose={onClose}
      size="large"
    >
      <SupplyInputForm
        onSubmit={(form) =>
          form &&
          createSupplyInputMutation
            .execute(entity.id, selectedYear, form)
            .then(onClose)
        }
      />
    </Dialog>
  )
}
