import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Box, Main } from "common/components/scaffold"
import { Trans, useTranslation } from "react-i18next"
import { useForm, Form } from "common/components/form2"
import { Button } from "common/components/button2"
import { useCessionDialog } from "./cession-dialog.hooks"
import { ElecCessionForm } from "./cession-dialog.types"
import { Autocomplete } from "common/components/autocomplete2"
import { normalizeEntityPreview } from "common/utils/normalizers"
import useEntity from "common/hooks/entity"
import { NumberInput } from "common/components/inputs2"
import { ElecBalance } from "accounting/types"
import { formatUnit } from "common/utils/formatters"
import { Unit } from "common/types"
import { Notice } from "common/components/notice"
import { findEligibleTiruertEntities } from "accounting/components/recipient-form/api"

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
          <Form
            id="elec-cession-form"
            form={form}
            onSubmit={() => mutation.execute()}
          >
            <Box>
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
            </Box>
            <Box>
              <NumberInput
                label={t("Quantité cédée (MJ)")}
                min={1}
                max={balance.available_balance}
                {...form.bind("quantity")}
                required
              />

              <Notice noColor variant="info">
                {t("Quantité disponible")}
                {" : "}
                <b>
                  {formatUnit(balance.available_balance, Unit.MJ, {
                    fractionDigits: 0,
                  })}
                </b>
              </Notice>
            </Box>
            <Box>
              <NumberInput
                label={t("Tonnes de CO2 évitées")}
                value={((form.value.quantity ?? 0) * 183) / 1e6}
                disabled
              />
            </Box>
          </Form>
        </Main>
      </Dialog>
    </Portal>
  )
}
