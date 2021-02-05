import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

export function clickOnCheckboxesAndConfirm() {
  userEvent.click(
    screen.getByLabelText(
      "Je certifie que cette déclaration respecte les critères de durabilité liés aux terres"
    )
  )

  userEvent.click(
    screen.getByLabelText(
      "Je certifie que les informations renseignées sont réelles et valides"
    )
  )

  userEvent.click(screen.getByText("Confirmer"))
}
