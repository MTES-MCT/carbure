import { Dialog } from "common/components/dialog2"
import { useHashMatch } from "common/components/hash-route"
import { useNavigate } from "react-router-dom"
import { useLocation } from "react-router-dom"
import useEntity from "common/hooks/entity"
import { useMutation, useQuery } from "common/hooks/async"
import { getSupplyInput, saveSupplyInput } from "../api"
import { useTranslation } from "react-i18next"
import { LoaderOverlay } from "common/components/scaffold"
import { Notice } from "common/components/notice"
import { SupplyInputForm } from "./supply-input-form"
import { Button } from "common/components/button2"

export const SupplyInputDialog = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("supply-input/:id")
  const entity = useEntity()
  const { t } = useTranslation()

  const supplyInputId = Number(match?.params.id)

  const { result: supplyInput, loading } = useQuery(getSupplyInput, {
    key: "supply-input",
    params: [entity.id, supplyInputId],
  })

  const saveSupplyInputMutation = useMutation(saveSupplyInput, {
    invalidates: ["supply-input", "supply-plan-inputs"],
  })

  const onClose = () => {
    navigate({ search: location.search, hash: "#" })
  }

  if (loading) {
    return <LoaderOverlay />
  }

  return (
    <Dialog
      header={
        <Dialog.Title>
          {t("Intrant n°{{id}}", { id: match?.params.id })}
        </Dialog.Title>
      }
      footer={
        <Button
          type="submit"
          loading={saveSupplyInputMutation.loading}
          nativeButtonProps={{ form: "supply-input-form" }}
        >
          {t("Valider l'intrant")}
        </Button>
      }
      onClose={onClose}
      size="large"
    >
      {!loading && !supplyInput ? (
        <Notice variant="warning" icon="ri-error-warning-line">
          {t("Intrant non trouvé")}
        </Notice>
      ) : (
        <SupplyInputForm
          supplyInput={supplyInput}
          onSubmit={(form) =>
            form &&
            saveSupplyInputMutation.execute(entity.id, supplyInputId, form)
          }
        />
      )}
    </Dialog>
  )
}
