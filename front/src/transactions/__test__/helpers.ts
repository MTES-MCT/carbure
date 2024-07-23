import { screen } from "@testing-library/react"
import { UserEvent } from "@testing-library/user-event/dist/types/setup/setup"

export async function clickOnCheckboxesAndConfirm(user: UserEvent) {
  await user.click(
    screen.getByLabelText(
      "Je certifie que cette déclaration respecte les critères de durabilité conformément à la réglementation en vigueur."
    )
  )

  await user.click(
    screen.getByLabelText(
      "Je certifie que les informations renseignées sont réelles et valides"
    )
  )

  const confirm = screen.getAllByText("Envoyer").pop()!
  expect(confirm).not.toBeDisabled()
  await user.click(confirm)
}
