import { simulate, simulateMinMax } from "accounting/api/operations"
import { Balance } from "accounting/types"
import { MutationOptions, useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { QuantityFormProps } from "./quantity-form.types"
import { apiTypes, FetchResponseType } from "common/services/api-fetch.types"
import { ExtendedUnit, Unit } from "common/types"
import { useUnit } from "common/hooks/unit"
import { FormManager } from "common/components/form2"
import { quantityFormStep } from "./quantity-form.utils"
import { FromDepotFormProps } from "../from-depot-form"
import { GHGRangeFormProps } from "../ghg-range-form/ghg-range-form"

type UseQuantityFormProps = {
  balance: Balance
  values: QuantityFormProps
  mutationOptions?: MutationOptions<
    FetchResponseType<apiTypes["SimulationMinMaxOutput"]>
  >
  unit?: Unit | ExtendedUnit
  // Custom conversion function for the backend (default is the value passed as parameter)
  converter?: (value: number) => number

  depotId?: number
  gesBoundMin?: number
  gesBoundMax?: number
}
export const useQuantityForm = ({
  balance,
  values,
  mutationOptions,
  unit: customUnit,
  converter = (value) => value,
  depotId,
  gesBoundMin,
  gesBoundMax,
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
      from_depot: depotId,
      ges_bound_min: gesBoundMin,
      ges_bound_max: gesBoundMax,
    })

  const mutation = useMutation(declareQuantity, mutationOptions)

  return mutation
}

type UseQuantityFormStepProps = {
  balance?: Balance
  // Unit of the quantity used by the backend (default is the entity preferred unit)
  backendUnit?: Unit | ExtendedUnit

  // Custom conversion function for the backend (default is the value passed as parameter)
  converter?: (value: number) => number
  form: FormManager<QuantityFormProps & FromDepotFormProps & GHGRangeFormProps>
  overrides?: Parameters<typeof quantityFormStep>[1]
}

export const useQuantityFormStep = ({
  balance,
  converter = (value) => value,
  form,
  backendUnit,
  overrides,
}: UseQuantityFormStepProps) => {
  const entity = useEntity()

  return quantityFormStep(form.value, {
    ...overrides,
    onClick: () => {
      if (!balance) return Promise.resolve()

      return simulate(entity.id, {
        biofuel: balance.biofuel.id,
        customs_category: balance.customs_category,
        debited_entity: entity.id,
        target_volume: converter(form.value.quantity!),
        target_emission: form.value.avoided_emissions ?? 0,
        from_depot: form.value.from_depot?.id,
        unit: backendUnit,
        ges_bound_min: form.value.gesBoundMin,
        ges_bound_max: form.value.gesBoundMax,
      }).then((response) => {
        form.setField("selected_lots", response.data?.selected_lots)
      })
    },
  })
}
