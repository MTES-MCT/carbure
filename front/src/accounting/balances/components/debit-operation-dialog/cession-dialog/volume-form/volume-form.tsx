import { Balance } from "accounting/balances/types"
import { useFormContext } from "common/components/form2"
import { useTranslation } from "react-i18next"
import { SessionDialogForm } from "../cession-dialog.types"

type VolumeFormProps = {
  balance: Balance
}

export const VolumeForm = ({ balance }: VolumeFormProps) => {
  const { t } = useTranslation()
  const { value, bind } = useFormContext<SessionDialogForm>()

  return <div>VolumeForm</div>
}
