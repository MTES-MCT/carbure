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
import { CONTRACT_FILE_MAX_SIZE } from "biomethane/config"

type AddContractForm = ReplaceNullWithUndefined<
  Pick<
    BiomethaneContractPatchRequest,
    "effective_date" | "signature_date" | "conditions_file"
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
  const { currentStep, mutation: addContractFiles } = useStepper()

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
          {currentStep?.key === "conditions_file" && (
            <Button
              loading={addContractFiles.loading}
              iconId="ri-send-plane-line"
              type="submit"
              nativeButtonProps={{ form: "add-contract-form" }}
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
          {currentStep?.key === "conditions_file" && (
            <FileInput
              {...form.bind("conditions_file")}
              required
              label={t("Conditions générales et particulières")}
              maxSize={CONTRACT_FILE_MAX_SIZE}
              accept=".pdf,.doc,.docx"
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
  const addContractFiles = useAddContract({
    onSuccess: props.onClose,
  })
  const handleSubmit = () => addContractFiles.execute(form.value)

  const steps = [
    {
      key: "dates",
      title: t("Dates"),
    },
    {
      key: "conditions_file",
      title: t("Conditions générales et particulières"),
      // Pass the onSubmit to the stepper, to run the function after the form is submitted and valid
      onSubmit: handleSubmit,
    },
  ]
  return (
    <StepperProvider steps={steps}>
      <AddContractContent {...props} form={form} />
    </StepperProvider>
  )
}
