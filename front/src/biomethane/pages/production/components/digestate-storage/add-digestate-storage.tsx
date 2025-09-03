import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form, useForm } from "common/components/form2"
import { NumberInput, RadioGroup, TextInput } from "common/components/inputs2"
import { Box } from "common/components/scaffold"
import { getYesNoOptions } from "common/utils/normalizers"
import { useTranslation } from "react-i18next"
import { BiomethaneDigestateStorageAddRequest } from "../../types"
import { useAddDigestateStorage } from "../../production.hooks"
import { DeepPartial } from "common/types"

type AddDigestateStorageForm = DeepPartial<BiomethaneDigestateStorageAddRequest>

interface AddDigestateStorageProps {
  onClose: () => void
}

export const AddDigestateStorage = ({ onClose }: AddDigestateStorageProps) => {
  const { t } = useTranslation()
  const { bind, value } = useForm<AddDigestateStorageForm>({
    type: "",
    capacity: 0,
    has_cover: false,
    has_biogas_recovery: false,
  })
  const { execute: addStorage, loading } = useAddDigestateStorage()

  const handleSubmit = async () => {
    if (value.type && value.capacity) {
      await addStorage(value)
      onClose()
    }
  }

  return (
    <Dialog
      size="medium"
      onClose={onClose}
      header={<Dialog.Title>{t("Ajouter un type de stockage")}</Dialog.Title>}
      footer={
        <Button
          iconId="ri-add-line"
          type="submit"
          loading={loading}
          nativeButtonProps={{
            form: "add-digestate-storage-form",
          }}
        >
          {t("Ajouter")}
        </Button>
      }
    >
      <Form id="add-digestate-storage-form" onSubmit={handleSubmit}>
        <Box>
          <TextInput
            required //
            label={t("Type de stockage")}
            {...bind("type")}
          />
          <NumberInput
            required
            type="number"
            label={t("Capacité de stockage (m3)")}
            {...bind("capacity")}
          />
          <RadioGroup
            required
            label={t("Couverture du stockage")}
            options={getYesNoOptions()}
            orientation="horizontal"
            {...bind("has_cover")}
          />
          <RadioGroup
            required
            label={t("Récupération du biogaz")}
            options={getYesNoOptions()}
            orientation="horizontal"
            {...bind("has_biogas_recovery")}
          />
        </Box>
      </Form>
    </Dialog>
  )
}
