import { renderHook } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { ExternalAdminPages } from "common/types"
import useEntity, { EntityManager } from "common/hooks/entity"
import { useUser, UserManager } from "common/hooks/user"
import { useBiomethanePermissions } from "./use-biomethane-permissions"

vi.mock("common/hooks/entity", () => ({
  default: vi.fn(),
}))

vi.mock("common/hooks/user", () => ({
  useUser: vi.fn(),
}))

const setup = ({
  isAuthenticated,
  grantedPages,
}: {
  isAuthenticated: boolean
  grantedPages: ExternalAdminPages[]
}) => {
  vi.mocked(useUser).mockReturnValue({
    isAuthenticated: () => isAuthenticated,
  } as Pick<UserManager, "isAuthenticated"> as UserManager)

  vi.mocked(useEntity).mockReturnValue({
    hasAnyAdminRight: (pages: ExternalAdminPages[]) =>
      pages.some((page) => grantedPages.includes(page)),
    hasAdminRight: (page: ExternalAdminPages) => grantedPages.includes(page),
    canWrite: () => true,
  } as Pick<
    EntityManager,
    "hasAnyAdminRight" | "hasAdminRight"
  > as EntityManager)
}

describe("useBiomethanePermissions", () => {
  it("canAccessAdmin is true only for DREAL and ADEME", () => {
    const allowedPages = new Set([
      ExternalAdminPages.DREAL,
      ExternalAdminPages.ADEME,
    ])
    const allPages = Object.values(ExternalAdminPages)

    for (const page of allPages) {
      setup({
        isAuthenticated: true,
        grantedPages: [page],
      })

      const { result } = renderHook(() => useBiomethanePermissions())

      expect(result.current.canAccessAdmin).toBe(allowedPages.has(page))
    }
  })

  it("canAccessAdmin is false if not authenticated", () => {
    setup({
      isAuthenticated: false,
      grantedPages: [ExternalAdminPages.DREAL, ExternalAdminPages.ADEME],
    })

    const { result } = renderHook(() => useBiomethanePermissions())

    expect(result.current.canAccessAdmin).toBe(false)
  })
})
