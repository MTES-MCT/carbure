import { renderHook } from "@testing-library/react"
import { ReactNode } from "react"
import { MemoryRouter, Route, Routes } from "react-router"
import { describe, expect, it } from "vitest"

import { useActionTabs } from "./use-action-tabs"

const tabs = [
  { key: "available", label: "Disponibles" },
  { key: "used", label: "Utilisés" },
]

function renderTabs(url: string) {
  return renderHook(() => useActionTabs(tabs), {
    wrapper: ({ children }: { children: ReactNode }) => (
      <MemoryRouter initialEntries={[url]}>
        <Routes>
          <Route path="/certificates/:year/:tab?" element={children} />
        </Routes>
      </MemoryRouter>
    ),
  })
}

describe("useActionTabs", () => {
  it("replaces the current tab segment in each link", () => {
    const { result } = renderTabs("/certificates/2026/available")

    expect(result.current.activeTab?.key).toBe("available")
    expect(result.current.redirect).toBeNull()
    expect(result.current.links?.map((link) => link.path)).toEqual([
      "/certificates/2026/available",
      "/certificates/2026/used",
    ])
  })

  it("appends the first tab when the URL has no tab segment", () => {
    const { result } = renderTabs("/certificates/2026")

    expect(result.current.redirect?.props.to.pathname).toBe(
      "/certificates/2026/available"
    )
  })

  it.each(["(", ")", "[", "+", "*", "?", ".*", "a+b", "a|b", "\\"])(
    "replaces an unexpected tab segment %j without throwing",
    (segment) => {
      const { result } = renderTabs(
        `/certificates/2026/${encodeURIComponent(segment)}`
      )

      expect(result.current.activeTab).toBeUndefined()
      expect(result.current.redirect?.props.to.pathname).toBe(
        "/certificates/2026/available"
      )
      expect(result.current.links?.map((link) => link.path)).toEqual([
        "/certificates/2026/available",
        "/certificates/2026/used",
      ])
    }
  )
})
