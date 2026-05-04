import { simulate, simulateMinMax } from "accounting/api/biofuels/operations"
import { Balance } from "accounting/types"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { QuantityFormProps } from "./quantity-form.types"
import { ExtendedUnit, ExtendedUnitType } from "common/types"
import { useUnit } from "common/hooks/unit"
import { FormManager } from "common/components/form2"
import { quantityFormStep } from "./quantity-form.utils"
import { GHGRangeFormProps } from "../ghg-range-form"
import { useRef } from "react"
// import { GHGRangeFormProps } from "../ghg-range-form"

type UseQuantityFormProps = {
  balance: Balance
  values: QuantityFormProps
  unit?: ExtendedUnitType
  depotId?: number
  gesBoundMin?: number
  gesBoundMax?: number
}
export const useQuantityForm = ({
  balance,
  values,
  unit: overrideUnit,
  depotId,
  gesBoundMin,
  gesBoundMax,
}: UseQuantityFormProps) => {
  const entity = useEntity()
  const { unit } = useUnit(overrideUnit)

  const declareQuantity = () =>
    simulateMinMax(entity.id, {
      biofuel: balance.biofuel?.id ?? null,
      customs_category: balance.customs_category,
      debited_entity: entity.id,
      target_volume: values.quantity!,
      target_emission: 0,
      unit,
      from_depot: depotId,
      ges_bound_min: gesBoundMin,
      ges_bound_max: gesBoundMax,
    })

  const mutation = useMutation(declareQuantity)

  return mutation
}

type UseQuantityFormStepProps = {
  balance?: Balance
  // Override the unit (default is the entity preferred unit)
  unit?: ExtendedUnit
  form: FormManager<QuantityFormProps & GHGRangeFormProps>
  overrides?: Parameters<typeof quantityFormStep>[1]
}

export const useQuantityFormStep = ({
  balance,
  unit: overrideUnit,
  form,
  overrides,
}: UseQuantityFormStepProps) => {
  const entity = useEntity()
  const { unit } = useUnit(overrideUnit)

  return quantityFormStep(form.value, {
    ...overrides,
    allowNextStep:
      form.value.avoided_emissions_min !== undefined &&
      form.value.avoided_emissions_max !== undefined,
    onSubmit: () => {
      if (!balance) return Promise.resolve()

      return simulate(entity.id, {
        biofuel: balance.biofuel.id,
        customs_category: balance.customs_category,
        debited_entity: entity.id,
        target_volume: form.value.quantity!,
        target_emission: form.value.avoided_emissions ?? 0,
        unit,
        ges_bound_min: form.value.gesBoundMin,
        ges_bound_max: form.value.gesBoundMax,
      }).then((response) => {
        form.setField("selected_lots", response.data?.selected_lots)
      })
    },
  })
}

export const useFocusOnAvoidedEmissions = () => {
  const avoidedEmissionsInputRef = useRef<HTMLInputElement>(null)

  const handleQuantityDeclared = () => {
    // Wait for the avoided emissions input to be mounted
    requestAnimationFrame(() => {
      avoidedEmissionsInputRef.current?.focus()
    })
  }

  return {
    avoidedEmissionsInputRef,
    handleQuantityDeclared,
  }
}
