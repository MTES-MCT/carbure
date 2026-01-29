import { useMutation } from "common/hooks/async"
import { validateQualichargeVolumes } from "../api"
import useEntity from "common/hooks/entity"
import { QualichargeQuery, QualichargeValidatedBy } from "../types"
import { ExternalAdminPages } from "common/types"

export type UseValidateVolumesProps = {
  onSuccess: () => void
}
export const useValidateVolumes = ({ onSuccess }: UseValidateVolumesProps) => {
  const entity = useEntity()
  const validateVolumes = useMutation(validateQualichargeVolumes, {
    invalidates: ["qualicharge-data"],
    onSuccess,
  })

  const validator =
    entity.isAdmin || entity.hasAdminRight(ExternalAdminPages.ELEC)
      ? QualichargeValidatedBy.DGEC
      : entity.isCPO
        ? QualichargeValidatedBy.CPO
        : undefined

  // When query is provided, we validate all data for the given query
  // Otherwise, we validate the given volumes
  const handleValidateVolumes = (
    volumes: number[],
    query?: QualichargeQuery
  ) => {
    if (validator) {
      return validateVolumes.execute(entity.id, volumes, validator, query)
    }

    return Promise.resolve()
  }

  return {
    loading: validateVolumes.loading,
    handleValidateVolumes,
  }
}
