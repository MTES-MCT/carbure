import { BiomethaneContract } from "biomethane/pages/contract/types"
import { BiomethaneEnergyInputRequest } from "biomethane/pages/energy/types"
import { useFormContext } from "common/components/form2"
import { CheckboxGroup } from "common/components/inputs2"
import { useEnergyTypeLabel, useEnergyTypeOptions } from "./energy-types.hooks"

type EnergyTypesProps = {
  contract?: BiomethaneContract
  isReadOnly?: boolean
}

type EnergyTypesForm = Pick<BiomethaneEnergyInputRequest, "energy_types">

export const EnergyTypes = ({ contract, isReadOnly }: EnergyTypesProps) => {
  const { bind, value } = useFormContext<EnergyTypesForm>()
  const energyTypeLabel = useEnergyTypeLabel(contract?.tariff_reference)
  const energyTypeOptions = useEnergyTypeOptions(contract)

  return (
    <CheckboxGroup
      {...bind("energy_types", {
        value: value?.energy_types ?? [],
      })}
      label={energyTypeLabel}
      options={energyTypeOptions}
      readOnly={isReadOnly}
    />
  )
}
