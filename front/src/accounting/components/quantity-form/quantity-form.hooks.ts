import { simulateMinMax } from "accounting/api/operations"
import { Balance } from "accounting/types"
import { MutationOptions, useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { QuantityFormProps } from "./quantity-form.types"
import { apiTypes, FetchResponseType } from "common/services/api-fetch.types"
import { ExtendedUnit, Unit } from "common/types"
import { useUnit } from "common/hooks/unit"

type UseQuantityFormProps = {
  balance: Balance
  values: QuantityFormProps
  mutationOptions?: MutationOptions<
    FetchResponseType<apiTypes["SimulationMinMaxOutput"]>
  >
  unit?: Unit | ExtendedUnit
  // Custom conversion function for the backend (default is the value passed as parameter)
  converter?: (value: number) => number
}
export const useQuantityForm = ({
  balance,
  values,
  mutationOptions,
  unit: customUnit,
  converter = (value) => value,
}: UseQuantityFormProps) => {
  const entity = useEntity()
  const { unit } = useUnit(customUnit)

  const declareQuantity = () =>
    simulateMinMax(entity.id, {
      biofuel: balance.biofuel?.id ?? null,
      customs_category: balance.customs_category,
      debited_entity: entity.id,
      target_volume: converter(values.quantity!),
      target_emission: 0,
      unit: unit,
    })

  const mutation = useMutation(declareQuantity, mutationOptions)

  return mutation
}
