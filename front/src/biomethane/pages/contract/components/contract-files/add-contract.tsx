import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { FormManager, useForm } from "common/components/form2"
import { DateInput, FileInput } from "common/components/inputs2"
import { Box, Grid } from "common/components/scaffold"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import { ReplaceNullWithUndefined } from "common/types"
import { useTranslation } from "react-i18next"
import { useAddContract } from "./add-contract.hooks"
import {
  BiomethaneContract,
  BiomethaneContractPatchRequest,
} from "biomethane/pages/contract/types"
import { getSignatureDateConstraints } from "./add-contract.utils"

type AddContractForm = ReplaceNullWithUndefined<
  Pick<
    BiomethaneContractPatchRequest,
    | "effective_date"
    | "signature_date"
    | "general_conditions_file"
    | "specific_conditions_file"
  >
>

interface AddContractProps {
  onClose: () => void
  contract?: BiomethaneContract
}

interface AddContractContentProps extends AddContractProps {
  form: FormManager<AddContractForm>
}

const AddContractContent = ({
  onClose,
  form,
  contract,
}: AddContractContentProps) => {
  const { t } = useTranslation()
  const { currentStep } = useStepper()
  const addContractFiles = useAddContract({
    onSuccess: onClose,
  })

  const handleSubmit = () => {
    addContractFiles.execute(form.value)
  }

  const signatureDateConstraints = getSignatureDateConstraints(
    contract?.tariff_reference
  )

  return (
    <Dialog
      header={<Dialog.Title>{t("Charger un contrat")}</Dialog.Title>}
      footer={
        <>
          <Stepper.Previous />
          <Stepper.Next nativeButtonProps={{ form: "add-contract-form" }} />
          {currentStep?.key === "specific" && (
            <Button
              onClick={handleSubmit}
              loading={addContractFiles.loading}
              iconId="ri-send-plane-line"
            >
              {t("Transmettre le contrat")}
            </Button>
          )}
        </>
      }
      size="medium"
      onClose={onClose}
    >
      <Stepper />
      <Box>
        <Stepper.Form form={form} id="add-contract-form">
          {currentStep?.key === "dates" && (
            <Grid cols={2} gap="lg">
              <DateInput
                label={t("Date de signature")}
                required
                {...form.bind("signature_date")}
                {...signatureDateConstraints}
              />
              <DateInput
                label={t("Date de prise d'effet")}
                required
                min={form.value.signature_date}
                {...form.bind("effective_date")}
              />
            </Grid>
          )}
          {currentStep?.key === "general" && (
            <FileInput
              required
              label={t("Conditions générales")}
              {...form.bind("general_conditions_file")}
            />
          )}
          {currentStep?.key === "specific" && (
            <FileInput
              required
              label={t("Conditions particulières")}
              {...form.bind("specific_conditions_file")}
            />
          )}
        </Stepper.Form>
      </Box>
    </Dialog>
  )
}

export const AddContract = (props: AddContractProps) => {
  const { t } = useTranslation()
  const form = useForm<AddContractForm>({})
  const steps = [
    {
      key: "dates",
      title: t("Dates"),
    },
    {
      key: "general",
      title: t("Conditions générales"),
      allowNextStep: Boolean(form.value.general_conditions_file),
    },
    {
      key: "specific",
      title: t("Conditions particulières"),
      allowNextStep: Boolean(form.value.specific_conditions_file),
    },
  ]
  return (
    <StepperProvider steps={steps}>
      <AddContractContent {...props} form={form} />
    </StepperProvider>
  )
}
