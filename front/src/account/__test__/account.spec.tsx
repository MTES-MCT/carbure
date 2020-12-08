import { rest } from "msw"
import { setupServer } from "msw/node"
import { render, waitFor, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { Entity, EntityType, UserRightStatus } from "common/types"

import Account from "../index"
import { useGetSettings } from "carbure/hooks/use-app"

const modal = document.createElement("div")
modal.setAttribute("id", "modal")

const dropdown = document.createElement("div")
dropdown.setAttribute("id", "dropdown")

document.body.append(modal, dropdown)

const producer: Entity = {
  id: 0,
  name: "Producteur Test",
  entity_type: EntityType.Producer,
  has_mac: true,
  has_trading: true,
  national_system_certificate: "",
}

const trader: Entity = {
  id: 1,
  name: "Trader Test",
  entity_type: EntityType.Trader,
  has_mac: true,
  has_trading: true,
  national_system_certificate: "",
}

let requests = [
  { entity: producer, date: new Date(), status: UserRightStatus.Accepted },
]

const server = setupServer(
  rest.get("/api/v3/settings", (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: {
          email: "producer@test.com",
          rights: [{ entity: producer, rights: "rw" }],
          requests,
        },
      })
    )
  }),
  rest.get("/api/v3/common/entities", (req, res, ctx) => {
    return res(
      ctx.json({
        status: "success",
        data: [producer, trader],
      })
    )
  }),
  rest.post("/api/v3/settings/request-entity-access", (req, res, ctx) => {
    requests = [
      ...requests,
      { entity: trader, date: new Date(), status: UserRightStatus.Pending },
    ]
    // console.log("cuicui", requests)
    return res(ctx.json({ status: "success" }))
  })
)

beforeAll(() => server.listen())

afterEach(() => {
  server.resetHandlers()
  modal.textContent = ""
  dropdown.textContent = ""

  requests = [
    { entity: producer, date: new Date(), status: UserRightStatus.Accepted },
  ]
})

afterAll(() => server.close())

// this component is only here for testing as otherwise we can't use the useGetSettingsHook
// because hooks can only work inside components
const AccountWithSettings = () => {
  const settings = useGetSettings()
  return <Account settings={settings} />
}

test("load the account page", async () => {
  render(<AccountWithSettings />)

  screen.getByText("Demande d'accès")
  screen.getByText("Identifiants")

  // wait for fake api to load
  await waitFor(() => {
    // check the first row of request access
    screen.getByText("Accepté")
    screen.getByText("Producteur Test")
    screen.getByText("Producteur")

    // check the displayed email
    screen.getByDisplayValue("producer@test.com")
  })
})

test("use the access request menu", async () => {
  render(<AccountWithSettings />)

  const button = screen.getByText("Ajouter une organisation")
  userEvent.click(button)

  const input = await waitFor(() =>
    screen.getByLabelText("Organisation", { selector: "input" })
  )

  userEvent.type(input, "Test")

  // test that the autocomplete is working nicely
  const traderOption = await waitFor(() => {
    expect(input.getAttribute("value")).toBe("Test")
    screen.getByText("Producteur Test", { selector: "li > *" })
    return screen.getByText("Trader Test")
  })

  // click an the Trader option to select it
  userEvent.click(traderOption)

  await waitFor(() => {
    // verify that the input has the selected value
    expect(input.getAttribute("value")).toBe("Trader Test")
  })

  // validate the choice by clicking the submit button
  userEvent.click(screen.getByText("Demander l'accès"))

  // check that the new access request is listed in the table
  await waitFor(() => {
    screen.getByText("En attente")
    screen.getByText("Trader Test")
    screen.getByText("Trader")
  })
})
