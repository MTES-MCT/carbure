import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form, FormManager, useForm } from "common/components/form2"
import { DateInput, FileInput } from "common/components/inputs2"
import { Box, Grid } from "common/components/scaffold"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import { ReplaceNullWithUndefined } from "common/types"
import { useTranslation } from "react-i18next"
import { useAddContract } from "./add-contract.hooks"
import { BiomethaneContractPatchRequest } from "biomethane/pages/contract/types"

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
}

interface AddContractContentProps extends AddContractProps {
  form: FormManager<AddContractForm>
}

const AddContractContent = ({ onClose, form }: AddContractContentProps) => {
  const { t } = useTranslation()
  const { currentStep } = useStepper()
  const addContractFiles = useAddContract({
    onSuccess: onClose,
  })

  const handleSubmit = () => {
    addContractFiles.execute(form.value)
  }

  return (
    <Dialog
      header={<Dialog.Title>{t("Charger un contrat")}</Dialog.Title>}
      footer={
        <>
          <Stepper.Previous />
          <Stepper.Next />
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
        <Form form={form}>
          {currentStep?.key === "dates" && (
            <Grid cols={2} gap="lg">
              <DateInput
                required
                label={t("Date de signature")}
                {...form.bind("signature_date")}
              />
              <DateInput
                required
                label={t("Date de prise d'effet")}
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
        </Form>
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
      allowNextStep:
        Boolean(form.value.effective_date) &&
        Boolean(form.value.signature_date),
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
