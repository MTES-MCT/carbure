import { simulateMinMax } from "accounting/api"
import { Balance } from "accounting/types"
import { MutationOptions, useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { QuantityFormProps } from "./quantity-form.types"
import { apiTypes, FetchResponseType } from "common/services/api-fetch.types"

type UseQuantityFormProps = {
  balance: Balance
  values: QuantityFormProps
  mutationOptions?: MutationOptions<
    FetchResponseType<apiTypes["SimulationMinMaxOutput"]>
  >
}
export const useQuantityForm = ({
  balance,
  values,
  mutationOptions,
}: UseQuantityFormProps) => {
  const entity = useEntity()

  const declareQuantity = () =>
    simulateMinMax(entity.id, {
      biofuel: balance.biofuel?.id ?? null,
      customs_category: balance.customs_category,
      debited_entity: entity.id,
      target_volume: values.quantity!,
      target_emission: 0,
      unit: entity.preferred_unit,
    })

  const mutation = useMutation(declareQuantity, mutationOptions)

  return mutation
}
