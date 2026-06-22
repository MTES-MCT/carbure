import { api } from "common/services/api-fetch"
import { ActionCreateRequest } from "./types"

export const getActionTree = async (entity_id: number) =>
  api
    .GET("/stock-poc/actions/tree/", { params: { query: { entity_id } } })
    .then((res) => res.data ?? [])

export const createAction = async (
  entity_id: number,
  body: ActionCreateRequest
) =>
  api
    .POST("/stock-poc/actions/", { params: { query: { entity_id } }, body })
    .then((res) => res.data)

export const updateAction = async (
  entity_id: number,
  action_id: number,
  body: Partial<ActionCreateRequest>
) =>
  api
    .PATCH("/stock-poc/actions/{id}/", {
      params: { path: { id: action_id }, query: { entity_id } },
      body,
    })
    .then((res) => res.data)

export const resetAllActions = async (entity_id: number) =>
  api
    .POST("/stock-poc/actions/reset/", {
      params: { query: { entity_id } },
    })
    .then((res) => res.data)

export const deleteAction = async (entity_id: number, action_id: number) =>
  api.DELETE("/stock-poc/actions/{id}/", {
    params: { path: { id: action_id }, query: { entity_id } },
  })
