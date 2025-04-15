import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Box, Main } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
import { useForm, Form } from "common/components/form2"
import { Button } from "common/components/button2"
import { useElecTeneurDialog } from "./declare-elec-teneur-dialog.hooks"
import { ElecTeneurForm } from "./declare-elec-teneur-dialog.types"
import { NumberInput } from "common/components/inputs2"
import { ElecCategoryObjective } from "../../types"

interface DeclareElecTeneurDialogProps {
  objective: ElecCategoryObjective
  onClose: () => void
}

export const DeclareElecTeneurDialog = ({
  objective,
  onClose,
}: DeclareElecTeneurDialogProps) => {
  const { t } = useTranslation()

  const form = useForm<ElecTeneurForm>({})
  const mutation = useElecTeneurDialog({ values: form.value, onClose })

  return (
    <Portal>
      <Dialog
        fullWidth
        onClose={onClose}
        header={
          <Dialog.Title>
            <Trans>Déclarer une teneur</Trans>
          </Dialog.Title>
        }
        footer={
          <Button
            type="submit"
            priority="primary"
            loading={mutation.loading}
            nativeButtonProps={{ form: "elec-teneur-form" }}
          >
            {t("Déclarer la teneur")}
          </Button>
        }
      >
        <Main>
          <Box>
            <Form
              id="elec-teneur-form"
              form={form}
              onSubmit={() => mutation.execute()}
            >
              <NumberInput
                label={t("Quantité déclarée en teneur (MJ)")}
                min={0.001}
                max={objective.quantity_available}
                step={0.001}
                {...form.bind("quantity")}
                required
              />
              <NumberInput
                label={t("Tonnes de CO2 évitées")}
                value={((form.value.quantity ?? 0) * 183) / 1e6}
                disabled
              />
            </Form>
          </Box>
        </Main>
      </Dialog>
    </Portal>
  )
}
