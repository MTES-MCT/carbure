import { getCompanyDetails } from "common/api"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import CompanyInfo from "settings/pages/company-info"

export const Contact = () => {
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()

  const { result, loading } = useQuery(getCompanyDetails, {
    key: "entity-details",
    params: [entity.id, selectedEntityId!],
  })

  if (!selectedEntityId) {
    throw new Error("Selected entity ID is required")
  }

  if (loading) {
    return <LoaderOverlay />
  }

  return <CompanyInfo readOnly company={result?.data} />
}
