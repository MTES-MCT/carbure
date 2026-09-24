import { renderToStaticMarkup } from "react-dom/server"
import { describe, expect, it, vi } from "vitest"
import { balance, balanceBiofuel } from "accounting/__test__/data/balances"
import { RecapOperation } from "./recap-operation"

vi.mock("react-i18next", async (importOriginal) => ({
  ...(await importOriginal<typeof import("react-i18next")>()),
  useTranslation: () => ({ t: (value: string) => value }),
}))

describe("RecapOperation", () => {
  it("displays PCI and a partial renewable share as a percentage", () => {
    const markup = renderToStaticMarkup(
      <RecapOperation
        balance={{
          ...balance,
          biofuel: { ...balanceBiofuel, renewable_energy_share: 0.5 },
        }}
      />
    )

    expect(markup).toContain("PCI")
    expect(markup).toContain("21,1 MJ/L")
    expect(markup).toContain("Taux renouvelable")
    expect(markup).toContain("50 %")
  })

  it("hides the renewable share when it is 100 percent", () => {
    const markup = renderToStaticMarkup(
      <RecapOperation
        balance={{
          ...balance,
          biofuel: { ...balanceBiofuel, renewable_energy_share: 1 },
        }}
      />
    )

    expect(markup).toContain("PCI")
    expect(markup).not.toContain("Taux renouvelable")
  })
})
