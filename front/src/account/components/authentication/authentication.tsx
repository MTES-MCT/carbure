import { ChangePasswordForm } from "./change-password-form"
import { ChangeEmailForm } from "./change-email-form"

export const AccountAuthentication = () => {
  return (
    <>
      <ChangeEmailForm />
      <ChangePasswordForm />
    </>
  )
}
