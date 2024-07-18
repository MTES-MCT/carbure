import { getUserRoleOptions } from "carbure/utils/normalizers"
import Dialog from "common/components/dialog"
import Button from "common/components/button"
import Form, { useForm } from "common/components/form"
import { type PortalInstance } from "common/components/portal"
import { RadioGroup } from "common/components/radio"
import { useTranslation } from "react-i18next"
import { TextInput } from "common/components/input"
import { Mail, Plus, Return } from "common/components/icons"
import { UserRole } from "carbure/types"

type AddUserDialogProps = {
  onClose: PortalInstance["close"]
}

export const AddUserDialog = ({ onClose }: AddUserDialogProps) => {
  const { t } = useTranslation()
  const { value, bind } = useForm<{
    email: string | undefined
    role: string | undefined
  }>({
    email: "",
    role: UserRole.ReadOnly,
  })

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Ajouter un utilisateur")}</h1>
      </header>
      <main>
        <section>{t("Veuillez remplir les informations suivantes")}</section>
        <section>
          <Form id="add-user" onSubmit={() => {}}>
            <TextInput
              variant="solid"
              icon={Mail}
              type="email"
              label={t("Adresse email")}
              {...bind("email")}
            />
            <RadioGroup
              label={t("Rôle")}
              options={getUserRoleOptions()}
              {...bind("role")}
            />
          </Form>
        </section>
      </main>
      <footer>
        <Button
          variant="primary"
          loading={false} // TODO
          icon={Plus}
          label={t("Ajouter")}
          disabled={!value.email || !value.role}
          submit="add-user"
        />
        <Button asideX icon={Return} action={onClose} label={t("Retour")} />
      </footer>
    </Dialog>
  )
}
