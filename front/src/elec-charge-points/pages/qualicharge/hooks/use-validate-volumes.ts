import { useMutation } from "common/hooks/async"
import { validateQualichargeVolumes } from "../api"
import useEntity from "common/hooks/entity"
import { QualichargeValidatedBy } from "../types"

export type UseValidateVolumesProps = {
  onSuccess: () => void
}
export const useValidateVolumes = ({ onSuccess }: UseValidateVolumesProps) => {
  const entity = useEntity()
  const validateVolumes = useMutation(validateQualichargeVolumes, {
    invalidates: ["qualicharge-data"],
    onSuccess,
  })

  const validator = entity.isAdmin
    ? QualichargeValidatedBy.DGEC
    : entity.isCPO
      ? QualichargeValidatedBy.CPO
      : undefined

  const handleValidateVolumes = (volumes: number[]) => {
    if (volumes.length > 0) {
      if (validator) {
        return validateVolumes.execute(entity.id, volumes, validator)
      }
    }
    return Promise.resolve()
  }

  return {
    loading: validateVolumes.loading,
    handleValidateVolumes,
  }
}
