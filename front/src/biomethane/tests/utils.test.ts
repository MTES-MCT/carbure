import { expect, test, describe, vi, beforeEach, afterEach } from "vitest"
import { getDeclarationInterval } from "../utils"

describe("getDeclarationInterval", () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2025, 7, 21)) // 21 août 2025
  })

  afterEach(() => {
    // Restaure les timers réels après chaque test
    vi.useRealTimers()
  })

  test("current declaration with date between 01/04/2025 - 31/12/2025 return current period year 2025", () => {
    const result = getDeclarationInterval()

    expect(result).toEqual({
      startDate: new Date(2025, 3, 1),
      endDate: new Date(2026, 2, 31),
      year: 2025,
    })
  })

  test("current declaration with date between 01/01/2026 - 03/04/2026 return current period year 2025", () => {
    vi.setSystemTime(new Date(2026, 1, 1))

    const result = getDeclarationInterval()

    expect(result).toEqual({
      startDate: new Date(2025, 3, 1),
      endDate: new Date(2026, 2, 31),
      year: 2025,
    })
  })
})
