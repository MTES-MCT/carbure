import { Autocomplete } from "common/components/autocomplete2"
import { Step } from "common/components/stepper"
import { Biofuel } from "common/types"
import i18next from "i18next"

export type BiofuelFormProps = {
  biofuel?: Biofuel
}

export const BiofuelForm = () => {
  return <Autocomplete />
}

export const biofuelFormStepKey = "biofuel"
type BiofuelFormStepKey = typeof biofuelFormStepKey

export const biofuelFormStep: (
  values: BiofuelFormProps
) => Step<BiofuelFormStepKey> = () => {
  return {
    key: biofuelFormStepKey,
    title: i18next.t("Biocarburant"),
    allowNextStep: true,
  }
}
