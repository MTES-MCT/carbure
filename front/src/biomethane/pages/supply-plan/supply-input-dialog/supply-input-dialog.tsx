import { Dialog } from "common/components/dialog2"
import { useHashMatch } from "common/components/hash-route"
import { useNavigate } from "react-router-dom"
import { useLocation } from "react-router-dom"
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { getSupplyInput } from "../api"
import { useTranslation } from "react-i18next"
import { LoaderOverlay } from "common/components/scaffold"
import { Notice } from "common/components/notice"
import { SupplyInputForm } from "./supply-input-form"

export const SupplyInputDialog = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const match = useHashMatch("supply-input/:id")
  const entity = useEntity()
  const { t } = useTranslation()
  const { result: supplyInput, loading } = useQuery(getSupplyInput, {
    key: `supply-input-${match?.params.id}`,
    params: [entity.id, Number(match?.params.id)],
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
      onClose={onClose}
      size="large"
    >
      {!loading && !supplyInput ? (
        <Notice variant="warning" icon="ri-error-warning-line">
          {t("Intrant non trouvé")}
        </Notice>
      ) : (
        <SupplyInputForm />
      )}
    </Dialog>
  )
}
