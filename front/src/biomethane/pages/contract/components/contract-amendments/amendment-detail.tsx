import { useQuery } from "common/hooks/async"
import { AddAmendment } from "./add-amendment"
import useEntity from "common/hooks/entity"
import { getAmendment } from "biomethane/pages/contract/api"
import { useHashMatch } from "common/components/hash-route"
import { LoaderOverlay } from "common/components/scaffold"
import { useNavigate } from "react-router-dom"
import { useRoutes } from "common/hooks/routes"

export const AmendmentDetail = () => {
  const entity = useEntity()
  const match = useHashMatch("amendment/:id")
  const navigate = useNavigate()
  const routes = useRoutes()
  const { result: amendment, loading } = useQuery(
    () => getAmendment(entity.id, Number(match?.params.id)),
    {
      key: `amendment-${match?.params.id}`,
      params: [],
    }
  )

  if (loading) {
    return <LoaderOverlay />
  }

  const initialData = {
    signature_date: amendment?.signature_date,
    effective_date: amendment?.effective_date,
    amendment_object: amendment?.amendment_object,
    amendment_details: amendment?.amendment_details,
  }

  return (
    <AddAmendment
      onClose={() => navigate(routes.SETTINGS.BIOMETHANE.CONTRACT)}
      readOnly
      initialData={initialData}
    />
  )
}
