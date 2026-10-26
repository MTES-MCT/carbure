import { cleanup, render, screen, fireEvent } from "@testing-library/react"
import { afterEach, describe, expect, it } from "vitest"
import {
  Link,
  MemoryRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
} from "react-router-dom"
import LegacyTabs from "./tabs"
import legacyCss from "./tabs.module.css"
import { Tabs } from "./tabs2"
import css from "./tabs2/tabs.module.css"
import { useLastSectorVisited } from "accounting/hooks/last-sector-visited"

afterEach(cleanup)

function Location() {
  const location = useLocation()
  return <output>{location.pathname + location.search + location.hash}</output>
}

for (const [name, Component, styles] of [
  ["legacy tabs", LegacyTabs, legacyCss],
  ["tabs2", Tabs, css],
] as const) {
  describe(name, () => {
    const activeClass = styles.active!
    it.each([
      [
        "/org/1/transactions/2026/in/pending",
        "/org/:entity/transactions/:year/*",
        "out",
        "/org/1/transactions/2026/out",
      ],
      [
        "/org/1/transactions/2026/stocks/pending",
        "/org/:entity/transactions/:year/stocks/*",
        "history",
        "/org/1/transactions/2026/stocks/history",
      ],
      [
        "/org/1/elec-admin-audit/2026/charge-points/pending",
        "/org/:entity/elec-admin-audit/:year/charge-points/*",
        "history",
        "/org/1/elec-admin-audit/2026/charge-points/history",
      ],
      [
        "/org/1/double-counting/agreements/active",
        "/org/:entity/double-counting/agreements/*",
        "pending",
        "/org/1/double-counting/agreements/pending",
      ],
      [
        "/org/1/accounting/operations/elec",
        "/org/:entity/accounting/*",
        "balances/biofuels",
        "/org/1/accounting/balances/biofuels",
      ],
      [
        "/org/1/charge-points/qualicharge/2026/pending",
        "/org/:entity/charge-points/qualicharge/:year/*",
        "validated",
        "/org/1/charge-points/qualicharge/2026/validated",
      ],
      ["/module", "/module/*", "pending", "/module/pending"],
      ["/module/", "/module/*", "pending", "/module/pending"],
      ["/module/pending/", "/module/*", "history", "/module/history"],
      ["/module/pending/detail/123", "/module/*", "history", "/module/history"],
      ["/module/caf%C3%A9", "/module/*", "history", "/module/history"],
      ["/module/a%2Fb", "/module/*", "history", "/module/history"],
      ["/module/a%252Fb", "/module/*", "history", "/module/history"],
      ["/module/a%25b", "/module/*", "history", "/module/history"],
      ["/module/a.b+(c)", "/module/*", "history", "/module/history"],
      ["/pending/pending", "/pending/*", "history", "/pending/history"],
      ["/pending", "/*", "history", "/history"],
      [
        "/org/caf%C3%A9/module/pending",
        "/org/:entity/module/*",
        "history",
        "/org/caf%C3%A9/module/history",
      ],
    ])("resolves a sibling tab at %s", (url, pattern, to, expected) => {
      render(
        <MemoryRouter initialEntries={[url]}>
          <Routes>
            <Route
              path={pattern}
              element={
                <Component
                  tabs={[{ key: "next", label: "Next tab", path: to }]}
                />
              }
            />
          </Routes>
        </MemoryRouter>
      )
      expect(screen.getByRole("link").getAttribute("href")).toBe(expected)
    })

    it("keeps nested tab bars relative to their own wildcard routes", () => {
      const tabs = [
        { key: "pending", label: "Pending", path: "pending" },
        { key: "history", label: "History", path: "history" },
      ]
      render(
        <MemoryRouter initialEntries={["/org/1/module/list/pending"]}>
          <Routes>
            <Route
              path="/org/:entity/*"
              element={
                <Routes>
                  <Route
                    path="module/*"
                    element={
                      <>
                        <Component
                          tabs={[{ key: "list", label: "List", path: "list" }]}
                        />
                        <Routes>
                          <Route
                            path="list/*"
                            element={<Component tabs={tabs} />}
                          />
                        </Routes>
                      </>
                    }
                  />
                </Routes>
              }
            />
          </Routes>
        </MemoryRouter>
      )
      expect(
        screen.getByRole("link", { name: "List" }).getAttribute("href")
      ).toBe("/org/1/module/list")
      expect(
        screen
          .getByRole("link", { name: "List" })
          .classList.contains(activeClass)
      ).toBe(true)
      expect(
        screen
          .getByRole("link", { name: "Pending" })
          .classList.contains(activeClass)
      ).toBe(true)
      expect(
        screen.getByRole("link", { name: "History" }).getAttribute("href")
      ).toBe("/org/1/module/list/history")
    })

    it("uses an inherited wildcard in a pathless accounting layout", () => {
      render(
        <MemoryRouter initialEntries={["/org/1/accounting/operations/elec"]}>
          <Routes>
            <Route
              path="/org/:entity/accounting/*"
              element={
                <Routes>
                  <Route
                    element={
                      <>
                        <Component
                          tabs={[
                            {
                              key: "biofuels",
                              label: "Biofuels",
                              path: "operations/biofuels",
                            },
                            {
                              key: "elec",
                              label: "Electricity",
                              path: "operations/elec",
                            },
                          ]}
                        />
                        <Outlet />
                      </>
                    }
                  >
                    <Route
                      path="operations/:category"
                      element={<p>Operations</p>}
                    />
                  </Route>
                </Routes>
              }
            />
          </Routes>
        </MemoryRouter>
      )
      expect(
        screen.getByRole("link", { name: "Biofuels" }).getAttribute("href")
      ).toBe("/org/1/accounting/operations/biofuels")
      expect(
        screen
          .getByRole("link", { name: "Electricity" })
          .classList.contains(activeClass)
      ).toBe(true)
    })

    it("preserves the router basename", () => {
      render(
        <MemoryRouter basename="/app" initialEntries={["/app/module/pending"]}>
          <Routes>
            <Route
              path="module/*"
              element={
                <Component
                  tabs={[
                    { key: "pending", label: "Pending", path: "pending" },
                    { key: "history", label: "History", path: "history" },
                  ]}
                />
              }
            />
          </Routes>
        </MemoryRouter>
      )
      expect(
        screen
          .getByRole("link", { name: "Pending" })
          .classList.contains(activeClass)
      ).toBe(true)
      expect(
        screen.getByRole("link", { name: "History" }).getAttribute("href")
      ).toBe("/app/module/history")
    })

    it("preserves search parameters and updates the selected tab after navigation", () => {
      render(
        <MemoryRouter initialEntries={["/module/history?year=2026"]}>
          <Location />
          <Routes>
            <Route
              path="module/*"
              element={
                <Component
                  keepSearch
                  tabs={[
                    { key: "pending", label: "Pending", path: "pending" },
                    { key: "history", label: "History", path: "history" },
                  ]}
                />
              }
            />
          </Routes>
        </MemoryRouter>
      )
      const history = screen.getByRole("link", { name: "History" })
      const pending = screen.getByRole("link", { name: "Pending" })
      expect(history.classList.contains(activeClass)).toBe(true)
      expect(pending.classList.contains(activeClass)).toBe(false)
      expect(pending.getAttribute("href")).toBe("/module/pending?year=2026")
      fireEvent.click(pending)
      expect(screen.getByRole("status").textContent).toBe(
        "/module/pending?year=2026"
      )
      expect(pending.classList.contains(activeClass)).toBe(true)
      expect(history.classList.contains(activeClass)).toBe(false)
    })

    it("preserves router-relative parent navigation", () => {
      render(
        <MemoryRouter initialEntries={["/org/1/reports/2026"]}>
          <Routes>
            <Route
              path="/org/:entity/*"
              element={
                <Routes>
                  <Route
                    path="reports/:year"
                    element={
                      <Component
                        tabs={[
                          {
                            key: "settings",
                            label: "Settings",
                            path: "../settings",
                          },
                        ]}
                      />
                    }
                  />
                </Routes>
              }
            />
          </Routes>
        </MemoryRouter>
      )
      expect(screen.getByRole("link").getAttribute("href")).toBe(
        "/org/1/settings"
      )
    })

    it("keeps parent-relative tab selection with inherited wildcard params", () => {
      render(
        <MemoryRouter initialEntries={["/module/pending"]}>
          <Routes>
            <Route
              path="module/*"
              element={
                <Routes>
                  <Route
                    path=":status"
                    element={
                      <Component
                        tabs={[
                          {
                            key: "history",
                            label: "History",
                            path: "../history",
                          },
                          {
                            key: "pending",
                            label: "Pending",
                            path: "../pending",
                          },
                        ]}
                      />
                    }
                  />
                </Routes>
              }
            />
          </Routes>
        </MemoryRouter>
      )
      const history = screen.getByRole("link", { name: "History" })
      const pending = screen.getByRole("link", { name: "Pending" })
      expect(history.getAttribute("href")).toBe("/module/history")
      expect(pending.classList.contains(activeClass)).toBe(true)
      expect(history.classList.contains(activeClass)).toBe(false)
      fireEvent.click(history)
      expect(history.classList.contains(activeClass)).toBe(true)
      expect(pending.classList.contains(activeClass)).toBe(false)
    })

    it("preserves absolute links, hash links, and tabs without a path", () => {
      render(
        <MemoryRouter initialEntries={["/module/pending"]}>
          <Routes>
            <Route
              path="module/*"
              element={
                <Component
                  tabs={[
                    { key: "absolute", label: "Absolute", path: "/elsewhere" },
                    {
                      key: "external",
                      label: "External",
                      path: "https://example.org/",
                    },
                    { key: "anchor", label: "Anchor", path: "#details" },
                    { key: "local", label: "Local" },
                  ]}
                />
              }
            />
          </Routes>
        </MemoryRouter>
      )
      expect(
        screen.getByRole("link", { name: "Absolute" }).getAttribute("href")
      ).toBe("/elsewhere")
      expect(
        screen.getByRole("link", { name: "External" }).getAttribute("href")
      ).toBe("https://example.org/")
      expect(
        screen.getByRole("link", { name: "Anchor" }).getAttribute("href")
      ).toBe("#details")
      expect(screen.getByRole("button", { name: "Local" })).toBeTruthy()
    })
  })
}

describe("module redirects with Router 7", () => {
  it("redirects an unknown nested URL to the module default", () => {
    render(
      <MemoryRouter initialEntries={["/auth/unknown/nested"]}>
        <Routes>
          <Route
            path="auth/*"
            element={
              <Routes>
                <Route path="login" element={<p>Login page</p>} />
                <Route path="*" element={<Navigate replace to="../login" />} />
              </Routes>
            }
          />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.getByText("Login page")).toBeTruthy()
  })

  it("keeps the selected accounting sector when changing pages", () => {
    function Accounting() {
      const sector = useLastSectorVisited()
      return <Link to={`/org/1/accounting/balances/${sector}`}>Balances</Link>
    }

    render(
      <MemoryRouter initialEntries={["/org/1/accounting/operations/elec"]}>
        <Routes>
          <Route path="/org/:entity/accounting/*" element={<Accounting />} />
        </Routes>
      </MemoryRouter>
    )
    const link = screen.getByRole("link", { name: "Balances" })
    expect(link.getAttribute("href")).toBe("/org/1/accounting/balances/elec")
    fireEvent.click(link)
    expect(link.getAttribute("href")).toBe("/org/1/accounting/balances/elec")
  })
})
