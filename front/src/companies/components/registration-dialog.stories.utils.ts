import { userEvent, waitFor, within } from "@storybook/test"
import { http, HttpResponse } from "msw"
import { companyResult } from "companies/__test__/data"

const SIREN_VALID = "753461261"

/** Fill the SIREN field with 9 digits to trigger the API call (mock MSW). */
export const fillSirenAndWaitForResult = async (canvasElement: HTMLElement) => {
  const canvas = within(canvasElement)
  const input = await waitFor(() =>
    canvas.getByRole("textbox", { name: /SIREN de votre entreprise/i })
  )
  await userEvent.click(input)
  await userEvent.type(input, SIREN_VALID)

  // Wait for the result: either the company form is prefilled (company name) or the warning notice is displayed
  await waitFor(() => {
    const formPrefilled = canvas.queryByDisplayValue("Company Test")
    const notice = canvas.queryByText(/Ce SIREN est déjà utilisé/)
    if (formPrefilled || notice) return
  })
}

/**
 * API search-company response: same format as the backend (company_preview + warning optional).
 * Utilisé pour les stories et les mocks MSW du module companies.
 */
const companyPreviewPayload = {
  company_preview: companyResult,
}

export const searchCompanySuccess = http.post(
  "/api/entities/search-company/",
  () => HttpResponse.json(companyPreviewPayload)
)

/** API response with one entity in meta.entities (SIREN already used by 1 entity) */
export const searchCompanyOneEntityInMeta = http.post(
  "/api/entities/search-company/",
  () =>
    HttpResponse.json({
      ...companyPreviewPayload,
      warning: {
        code: "REGISTRATION_ID_ALREADY_USED",
        meta: {
          company_name: "Producteur Biométhane Île-de-France",
          entities: [
            {
              name: "Producteur Biométhane Île-de-France",
              entity_type: "Producteur de biométhane",
              registration_id: "75346126",
            },
          ],
        },
      },
    })
)

/** API response with multiple entities in meta.entities (SIREN already used by multiple entities) */
export const searchCompanySeveralEntitiesInMeta = http.post(
  "/api/entities/search-company/",
  () =>
    HttpResponse.json({
      ...companyPreviewPayload,
      warning: {
        code: "REGISTRATION_ID_ALREADY_USED",
        meta: {
          company_name: "Société Multi-Activités",
          entities: [
            {
              name: "Société Multi-Activités - Producteur",
              entity_type: "Producteur",
              registration_id: "75346126",
            },
            {
              name: "Société Multi-Activités - Biométhane",
              entity_type: "Producteur de biométhane",
              registration_id: "75346126",
            },
          ],
        },
      },
    })
)

export const searchCompanyHandlers = [searchCompanySuccess]
