import { describe, expect, it } from "vitest"

import { ActionStatus, ActionType } from "traceability/types"
import { combineQueries } from "./use-combined-query"

describe("combineQueries", () => {
  it("keeps a base value when the override sends undefined", () => {
    const combined = combineQueries(
      {
        type: [ActionType.VALORIZE],
        status: [ActionStatus.CREATED],
        quantity_available: true,
      },
      { status: undefined, search: undefined }
    )

    expect(combined).toEqual({
      type: [ActionType.VALORIZE],
      status: [ActionStatus.CREATED],
      quantity_available: true,
    })
  })

  it("replaces a base value when the override defines the same key", () => {
    const combined = combineQueries(
      { type: [ActionType.VALORIZE], status: [ActionStatus.CREATED] },
      { type: [ActionType.TRANSFER] }
    )

    expect(combined).toEqual({
      type: [ActionType.TRANSFER],
      status: [ActionStatus.CREATED],
    })
  })

  it("adds filters that only the override defines", () => {
    const combined = combineQueries(
      { type: [ActionType.INIT] },
      { origin_material: ["renewable"], site: ["station"] }
    )

    expect(combined).toEqual({
      type: [ActionType.INIT],
      origin_material: ["renewable"],
      site: ["station"],
    })
  })
})
