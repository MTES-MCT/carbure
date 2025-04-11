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
            priority="primary"
            onClick={() => mutation.execute()}
            loading={mutation.loading}
          >
            {t("Céder")}
          </Button>
        }
      >
        <Main>
          <Box>
            <Form form={form}>
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
                label={t(
                  `Quantité cédée (MJ) - Disponible: ${balance.available_balance}`
                )}
                min={0}
                max={balance.available_balance}
                {...form.bind("quantity")}
                required
              />
            </Form>
          </Box>
        </Main>
      </Dialog>
    </Portal>
  )
}
