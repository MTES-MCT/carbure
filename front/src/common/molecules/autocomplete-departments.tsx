import { getDepartmentOptions } from "common/utils/geography"
import {
  Autocomplete,
  AutocompleteProps,
} from "common/components/autocomplete2"
import { useTranslation } from "react-i18next"

const departmentsOptions = getDepartmentOptions()

export const AutoCompleteDepartments = (
  props: AutocompleteProps<
    { label: string; value: string },
    string | null | undefined
  >
) => {
  const { t } = useTranslation()

  return (
    <Autocomplete
      placeholder={t("Rechercher un département...")}
      options={departmentsOptions}
      sort={(item) => item.value ?? ""}
      {...props}
    />
  )
}
