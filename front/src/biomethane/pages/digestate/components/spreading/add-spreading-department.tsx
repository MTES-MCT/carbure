import { Dialog } from "common/components/dialog2"
import { Form, useForm } from "common/components/form2"
import { Box } from "common/components/scaffold"
import { SelectDsfr } from "common/components/selects2"
import { getDepartmentOptions } from "common/utils/geography"
import { useTranslation } from "react-i18next"
import {
  BiomethaneDigestateSpreading,
  BiomethaneDigestateSpreadingAddRequest,
} from "../../types"
import { NumberInput } from "common/components/inputs2"
import { Button } from "common/components/button2"
import { addSpreadingDepartment } from "../../api"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useMemo } from "react"

const departmentOptions = getDepartmentOptions()

type AddSpreadingDepartmentForm =
  Partial<BiomethaneDigestateSpreadingAddRequest>

export const AddSpreadingDepartment = ({
  onClose,
  spreadings,
}: {
  onClose: () => void
  spreadings: BiomethaneDigestateSpreading[]
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { bind, value } = useForm<AddSpreadingDepartmentForm>({})
  const mutate = useMutation(addSpreadingDepartment, {
    invalidates: ["digestate"],
    onSuccess: () => {
      onClose()
    },
  })

  const handleSubmit = () => {
    mutate.execute(entity.id, {
      spreading_department: value.spreading_department!,
      spread_quantity: value.spread_quantity!,
      spread_parcels_area: value.spread_parcels_area!,
    })
  }

  const options = useMemo(() => {
    const departmentIds = spreadings.map(
      (spreading) => spreading.spreading_department
    )
    return departmentOptions
      .filter((option) => !departmentIds.includes(option.value))
      .sort((a, b) => a.value.localeCompare(b.value))
  }, [spreadings])

  return (
    <Dialog
      header={<Dialog.Title>{t("Ajouter un département")}</Dialog.Title>}
      onClose={onClose}
      footer={
        <Button
          type="submit"
          nativeButtonProps={{ form: "add-spreading-department-form" }}
          loading={mutate.loading}
        >
          {t("Ajouter")}
        </Button>
      }
      size="medium"
    >
      <Box>
        <Form id="add-spreading-department-form" onSubmit={handleSubmit}>
          <SelectDsfr
            options={options}
            label={t("Département")}
            placeholder={t("Sélectionner un département")}
            {...bind("spreading_department")}
            required
          />
          <NumberInput
            label={t("Quantité épandue (t)")}
            placeholder={t("Quantité épandue (t)")}
            {...bind("spread_quantity")}
            required
          />
          <NumberInput
            label={t("Superficie des parcelles épandues (ha)")}
            placeholder={t("Superficie des parcelles épandues (ha)")}
            {...bind("spread_parcels_area")}
            required
          />
        </Form>
      </Box>
    </Dialog>
  )
}
