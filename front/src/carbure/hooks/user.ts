import { createContext, useContext } from "react"
import { useQuery } from "common-v2/hooks/async"
import { Entity, UserRight, UserRightRequest } from "../types"
import * as api from "../api"
import { invalidate } from "common-v2/hooks/invalidate"

export interface UserManager {
  loading: boolean
  email: string
  rights: UserRight[]
  requests: UserRightRequest[]
  isAuthenticated: () => boolean
  getRights: (entityID: number) => UserRight | null
  hasEntity: (entityID: number) => boolean
  hasEntities: () => boolean
  getFirstEntity: () => Entity | null
}

export function useLoadUser(): UserManager {
  const settings = useQuery(api.getUserSettings, {
    key: "user-settings",
    params: [],
  })

  const res = settings.result?.data.data
  const email = res?.email ?? ""
  const rights = res?.rights ?? []
  const requests = res?.requests ?? []

  function getRights(entityID: number) {
    return rights?.find((r) => r.entity.id === entityID) ?? null
  }

  function hasEntity(entityID: number) {
    return Boolean(getRights(entityID))
  }

  function hasEntities() {
    return rights.length > 0
  }

  function getFirstEntity() {
    return rights[0]?.entity ?? null
  }

  function isAuthenticated() {
    return settings.result !== undefined && settings.error === undefined
  }

  return {
    loading: settings.loading,
    email,
    rights,
    requests,
    isAuthenticated,
    getRights,
    hasEntity,
    hasEntities,
    getFirstEntity,
  }
}

export const UserContext = createContext<UserManager | undefined>(undefined)

export function useUser() {
  const user = useContext(UserContext)
  if (user === undefined) throw new Error("User context is not defined")
  return user
}

export function reloadUserSettings() {
  invalidate("user-settings")
}

export default useLoadUser
