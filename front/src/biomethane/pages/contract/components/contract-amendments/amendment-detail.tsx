import { useQuery } from "common/hooks/async"
import { AmendmentObjectEnum } from "api-schema"
import { AddAmendment } from "./add-amendment"
import useEntity from "common/hooks/entity"
import { getAmendment } from "biomethane/api"

interface AmendmentDetailProps {
  amendmentId: number
  onClose: () => void
}

export const AmendmentDetail = ({
  amendmentId,
  onClose,
}: AmendmentDetailProps) => {
  const entity = useEntity()

  const {
    result: amendment,
    loading,
    error,
  } = useQuery(() => getAmendment(entity.id, amendmentId), {
    key: `amendment-${amendmentId}`,
    params: [],
  })

  if (loading) {
    return <div>Chargement...</div>
  }

  if (error || !amendment) {
    return <div>Erreur lors du chargement de l'avenant</div>
  }

  const amendmentObject = amendment.amendment_object.split(
    ","
  ) as AmendmentObjectEnum[]

  const initialData = {
    signature_date: amendment.signature_date,
    effective_date: amendment.effective_date,
    amendment_object: amendmentObject,
    amendment_details: amendment.amendment_details,
  }
  return (
    <AddAmendment onClose={onClose} readOnly={true} initialData={initialData} />
  )
}
