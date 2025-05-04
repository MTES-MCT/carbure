import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Box, Main } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
import { useForm, Form } from "common/components/form2"
import { Button } from "common/components/button2"
import { useCessionDialog } from "./cession-dialog.hooks"
import { ElecCessionForm } from "./cession-dialog.types"
import { findEligibleTiruertEntities } from "accounting/components/recipient-to-depot-form/api"
import { Autocomplete } from "common/components/autocomplete2"
import { normalizeEntityPreview } from "common/utils/normalizers"
import useEntity from "common/hooks/entity"
import { NumberInput } from "common/components/inputs2"
import { ElecBalance } from "accounting/types"
import Alert from "common/components/alert"
import { formatUnit } from "common/utils/formatters"
import { Unit } from "common/types"
import { InfoCircle } from "common/components/icons"

interface CessionDialogProps {
  balance: ElecBalance
  onClose: () => void
}

export const CessionDialog = ({ balance, onClose }: CessionDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const form = useForm<ElecCessionForm>({})

  const mutation = useCessionDialog({
    values: form.value,
    onClose,
  })

  return (
    <Portal>
      <Dialog
        fullWidth
        onClose={onClose}
        header={
          <Dialog.Title>
            <Trans>Réaliser une cession</Trans>
          </Dialog.Title>
        }
        footer={
          <Button
            type="submit"
            priority="primary"
            loading={mutation.loading}
            nativeButtonProps={{ form: "elec-cession-form" }}
          >
            {t("Céder")}
          </Button>
        }
      >
        <Main>
          <Box>
            <Form
              id="elec-cession-form"
              form={form}
              onSubmit={() => mutation.execute()}
            >
              <Autocomplete
                label={t("Sélectionnez un destinataire")}
                placeholder={t("Rechercher un destinataire")}
                getOptions={(query) =>
                  findEligibleTiruertEntities(entity.id, query)
                }
                normalize={normalizeEntityPreview}
                {...form.bind("credited_entity")}
                required
              />

              <NumberInput
                label={t("Quantité cédée (MJ)")}
                step={0.001}
                min={0.001}
                max={balance.available_balance}
                {...form.bind("quantity")}
                required
              />

              <Alert icon={InfoCircle} variant="info">
                {t("Quantité disponible")}
                {" : "}
                {formatUnit(balance.available_balance, Unit.MJ, {
                  fractionDigits: 0,
                })}
              </Alert>

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
