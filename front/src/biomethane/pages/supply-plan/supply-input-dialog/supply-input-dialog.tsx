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
import { useNotify, useNotifyError } from "common/components/notifications"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export const SupplyInputDialog = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("supply-input/:id")
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()
  const { t } = useTranslation()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { canEditDeclaration, selectedYear } = useAnnualDeclaration()
  const supplyInputId = Number(match?.params.id)

  const { result: supplyInput, loading } = useQuery(getSupplyInput, {
    key: "supply-input",
    params: [entity.id, supplyInputId, selectedEntityId],
  })

  const saveSupplyInputMutation = useMutation(saveSupplyInput, {
    invalidates: ["supply-input", "supply-plan-inputs"],
    onSuccess: () => {
      notify(t("Les détails de l'intrant ont bien été mis à jour."), {
        variant: "success",
      })
    },
    onError: (e) => {
      notifyError(e)
    },
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
        canEditDeclaration && (
          <Button
            type="submit"
            loading={saveSupplyInputMutation.loading}
            nativeButtonProps={{ form: "supply-input-form" }}
          >
            {t("Valider l'intrant")}
          </Button>
        )
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
            saveSupplyInputMutation
              .execute(entity.id, selectedYear, supplyInputId, form)
              .then(onClose)
          }
          readOnly={!canEditDeclaration}
        />
      )}
    </Dialog>
  )
}
