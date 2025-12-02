import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form, useForm } from "common/components/form2"
import { DateInput, FileInput, TextArea } from "common/components/inputs2"
import { CheckboxGroup } from "common/components/inputs2/checkbox/checkbox"
import { Box, Grid } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { addAmendment } from "biomethane/pages/contract/api"
import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import useEntity from "common/hooks/entity"
import { AmendmentObjectEnum } from "api-schema"
import { useAddAmendmentObjectOptions } from "./add-amendment.hooks"
import { EditableCard } from "common/molecules/editable-card"
import { BiomethaneAmendmentAddRequest } from "biomethane/pages/contract/types"
import { CONVERSIONS } from "common/utils/formatters"

type AddAmendmentForm = Partial<BiomethaneAmendmentAddRequest>

interface AddAmendmentProps {
  onClose: () => void
  readOnly?: boolean
  initialData?: AddAmendmentForm
}

export const AddAmendment = ({
  onClose,
  readOnly,
  initialData,
}: AddAmendmentProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const amendmentObjectOptions = useAddAmendmentObjectOptions()

  const form = useForm<AddAmendmentForm>({
    amendment_details: initialData?.amendment_details,
    amendment_object: initialData?.amendment_object ?? [],
    signature_date: initialData?.signature_date,
    effective_date: initialData?.effective_date,
    amendment_file: initialData?.amendment_file,
  })

  const addAmendmentMutation = useMutation(
    (data: AddAmendmentForm) =>
      addAmendment(entity.id, {
        signature_date: data.signature_date!,
        effective_date: data.effective_date!,
        amendment_object: data.amendment_object!,
        amendment_file: data.amendment_file!,
        amendment_details: data.amendment_details!,
      }),
    {
      invalidates: ["contract-infos"],
      onSuccess: () => {
        notify(t("L'avenant a bien été ajouté."), { variant: "success" })
        onClose()
      },
      onError: (e) => {
        notifyError(e)
      },
    }
  )

  const handleSubmit = () => {
    addAmendmentMutation.execute(form.value)
  }

  const hasOtherSelected = form.value.amendment_object?.includes(
    AmendmentObjectEnum.OTHER
  )

  return (
    <Dialog
      header={<Dialog.Title>{t("Avenants au contrat d'achat")}</Dialog.Title>}
      footer={
        !readOnly && (
          <Button
            loading={addAmendmentMutation.loading}
            iconId="ri-add-line"
            type="submit"
            nativeButtonProps={{
              form: "add-amendment-form",
            }}
          >
            {t("Ajouter un avenant")}
          </Button>
        )
      }
      size="medium"
      onClose={onClose}
    >
      <Form form={form} onSubmit={handleSubmit} id="add-amendment-form">
        <Box>
          <Grid cols={2} gap="lg">
            <DateInput
              required
              label={t("Date de signature")}
              {...form.bind("signature_date")}
              readOnly={readOnly}
            />
            <DateInput
              required
              label={t("Date de prise d'effet")}
              {...form.bind("effective_date")}
              readOnly={readOnly}
            />
          </Grid>

          <CheckboxGroup
            {...form.bind("amendment_object")}
            options={amendmentObjectOptions}
            label={t("Objet d'avenant")}
            hintText={t("Vous pouvez sélectionner plusieurs objets d'avenant")}
            readOnly={readOnly}
            required
          />

          {hasOtherSelected && (
            <TextArea
              label={t("Précisions")}
              {...form.bind("amendment_details")}
              value={form.value.amendment_details ?? ""}
              required
              readOnly={readOnly}
            />
          )}
        </Box>
        {!readOnly && (
          <EditableCard
            title={t("Déposer votre avenant ici")}
            headerActions={null}
          >
            <FileInput
              required
              value={form.value.amendment_file}
              onChange={(value) => form.setField("amendment_file", value)}
              label={t("Avenant au contrat")}
              maxSize={CONVERSIONS.bytes.MB_TO_BYTES(10)}
            />
          </EditableCard>
        )}
      </Form>
    </Dialog>
  )
}
