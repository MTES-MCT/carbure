import { renderHook } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { ActionStatus, ActionType } from "traceability/types"
import { useCombinedQuery } from "./use-combined-query"

describe("useCombinedQuery", () => {
  it("keeps a base value when a later query sends undefined", () => {
    const { result } = renderHook(() =>
      useCombinedQuery(
        {
          type: [ActionType.VALORIZE],
          status: [ActionStatus.CREATED],
          quantity_available: true,
        },
        { status: undefined, search: undefined }
      )
    )

    expect(result.current).toEqual({
      type: [ActionType.VALORIZE],
      status: [ActionStatus.CREATED],
      quantity_available: true,
    })
  })

  it("replaces a base value when a later query defines the same key", () => {
    const { result } = renderHook(() =>
      useCombinedQuery(
        { type: [ActionType.VALORIZE], status: [ActionStatus.CREATED] },
        { type: [ActionType.TRANSFER] }
      )
    )

    expect(result.current).toEqual({
      type: [ActionType.TRANSFER],
      status: [ActionStatus.CREATED],
    })
  })

  it("adds filters that only a later query defines", () => {
    const { result } = renderHook(() =>
      useCombinedQuery(
        { type: [ActionType.INIT] },
        { origin_material: ["renewable"], site: ["station"] }
      )
    )

    expect(result.current).toEqual({
      type: [ActionType.INIT],
      origin_material: ["renewable"],
      site: ["station"],
    })
  })

  it("merges more than two queries, each later query overriding the previous ones", () => {
    const { result } = renderHook(() =>
      useCombinedQuery(
        { type: [ActionType.INIT], status: [ActionStatus.CREATED] },
        { type: [ActionType.VALORIZE], origin_material: ["renewable"] },
        { type: [ActionType.TRANSFER], status: undefined, site: ["station"] }
      )
    )

    expect(result.current).toEqual({
      type: [ActionType.TRANSFER],
      status: [ActionStatus.CREATED],
      origin_material: ["renewable"],
      site: ["station"],
    })
  })
})
