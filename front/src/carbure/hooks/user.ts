import { createContext, useContext } from "react"
import { useQuery } from "common/hooks/async"
import { Entity, UserRight, UserRightStatus } from "../types"
import * as api from "../api"

export interface UserManager {
  loading: boolean
  email: string
  rights: UserRight[]
  isAuthenticated: () => boolean
  getRights: (entityID: number) => UserRight | null
  hasEntity: (entityID: number) => boolean
  hasEntities: () => boolean
  getFirstEntity: () => Entity | null
}

export function useUserManager(): UserManager {
  const settings = useQuery(api.getUserSettings, {
    key: "user-settings",
    params: [],
  })

  const res = settings.result?.data.data
  const email = res?.email ?? ""
  const rights = res?.rights ?? []

  function getRights(entityID: number) {
    return (
      rights?.find(
        (r) => r.entity.id === entityID && r.status === UserRightStatus.Accepted
      ) ?? null
    )
  }

  function hasEntity(entityID: number) {
    return Boolean(getRights(entityID))
  }

  function hasEntities() {
    return (
      rights.filter((r) => r.status === UserRightStatus.Accepted).length > 0
    )
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

export default useUserManager
