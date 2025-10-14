import { CreateOperationType } from "accounting/types"
import { useFormContext } from "common/components/form2"
import {
  QuantityFormProps,
  QuantitySummary as ExportationQuantitySummary,
  quantityFormStepKey as exportationQuantityFormStepKey,
  QuantityFormComponentProps,
  QuantityForm,
} from "accounting/components/quantity-form"

export type ExportationQuantityFormProps = Pick<
  QuantityFormProps,
  | "quantity"
  | "avoided_emissions_min"
  | "avoided_emissions_max"
  | "avoided_emissions"
>

type ExportationQuantityFormComponentProps = Pick<
  QuantityFormComponentProps,
  "balance" | "quantityMax" | "gesBoundMin" | "gesBoundMax"
>

export const ExportationQuantityForm = ({
  balance,
  quantityMax,
  gesBoundMin,
  gesBoundMax,
}: ExportationQuantityFormComponentProps) => {
  const { setField } = useFormContext<ExportationQuantityFormProps>()

  return (
    <QuantityForm
      balance={balance}
      quantityMax={quantityMax}
      type={CreateOperationType.EXPORTATION}
      gesBoundMin={gesBoundMin}
      gesBoundMax={gesBoundMax}
      onQuantityDeclared={(emissions) => {
        setField("avoided_emissions_min", emissions.emissionsMax)
        setField("avoided_emissions_max", emissions.emissionsMax)
        setField("avoided_emissions", emissions.emissionsMax)
      }}
    />
  )
}

export { ExportationQuantitySummary, exportationQuantityFormStepKey }
