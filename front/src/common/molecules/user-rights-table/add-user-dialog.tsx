import { getUserRoleOptions } from "common/utils/normalizers"
import Dialog from "common/components/dialog"
import Button from "common/components/button"
import Form, { useForm } from "common/components/form"
import { type PortalInstance } from "common/components/portal"
import { RadioGroup } from "common/components/radio"
import { useTranslation } from "react-i18next"
import { TextInput } from "common/components/input"
import { Mail, Plus, Return } from "common/components/icons"
import { UserRole } from "common/types"
import { useAsyncCallback } from "react-async-hook"
import { useNotify } from "common/components/notifications"

export type AddUserDialogProps = {
  onClose: PortalInstance["close"]
  onAddNewUser: (email: string, role: UserRole) => Promise<unknown>
}

export const AddUserDialog = ({
  onClose,
  onAddNewUser,
}: AddUserDialogProps) => {
  const { t } = useTranslation()
  const { value, bind, setFieldError } = useForm<{
    email: string | undefined
    role: UserRole | undefined
  }>({
    email: "",
    role: UserRole.ReadOnly,
  })
  const notify = useNotify()

  const addNewUserMutation = useAsyncCallback(onAddNewUser, {
    onSuccess: () => {
      onClose()
      notify(
        t("L'utilisateur {{email}} a bien été ajouté !", {
          email: value.email,
        }),
        {
          variant: "success",
        }
      )
      setFieldError("email", "")
    },
    onError: () => {
      setFieldError("email", t("Le format d'email n'est pas valide"))
    },
  })

  const handleSubmit = async () => {
    // Wait for backend request before closing dialog
    addNewUserMutation.execute(value.email!, value.role!)
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Ajouter un utilisateur")}</h1>
      </header>
      <main>
        <section>{t("Veuillez remplir les informations suivantes :")}</section>
        <section>
          <Form id="add-user" onSubmit={handleSubmit}>
            <TextInput
              variant="outline"
              icon={Mail}
              type="email"
              label={t("Adresse email")}
              hideError={false}
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
          icon={Plus}
          label={t("Ajouter")}
          disabled={!value.email || !value.role}
          loading={addNewUserMutation.loading}
          submit="add-user"
        />
        <Button asideX icon={Return} action={onClose} label={t("Retour")} />
      </footer>
    </Dialog>
  )
}
