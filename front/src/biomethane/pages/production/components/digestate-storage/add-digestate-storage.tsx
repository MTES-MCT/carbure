import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form } from "common/components/form2"
import { RadioGroup, TextInput } from "common/components/inputs2"
import { Box } from "common/components/scaffold"
import { getYesNoOptions } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"

interface AddDigestateStorageProps {
  onClose: () => void
}

export const AddDigestateStorage = ({ onClose }: AddDigestateStorageProps) => {
  const { t } = useTranslation()

  return (
    <Dialog
      size="medium"
      onClose={onClose}
      header={<Dialog.Title>{t("Ajouter un type de stockage")}</Dialog.Title>}
      footer={
        <Button
          iconId="ri-add-line"
          type="submit"
          nativeButtonProps={{
            form: "add-digestate-storage-form",
          }}
        >
          {t("Ajouter")}
        </Button>
      }
    >
      <Form id="add-digestate-storage-form">
        <Box>
          <TextInput
            required
            label={t("Type de stockage")}
            //
          />
          <TextInput
            required
            label={t("Capacité de stockage (m3)")}
            //
          />
          <RadioGroup
            label={t("Couverture du stockage")}
            options={getYesNoOptions()}
            orientation="horizontal"
          />
          <RadioGroup
            label={t("Récupération du biogaz")}
            options={getYesNoOptions()}
            orientation="horizontal"
          />
        </Box>
      </Form>
    </Dialog>
  )
}
