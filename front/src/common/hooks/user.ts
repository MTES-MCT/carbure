import { createContext, useContext } from "react"
import { useQuery } from "common/hooks/async"
import { Entity, User, UserRight, UserRightRequest } from "common/types"
import * as api from "common/api"
import * as Sentry from "@sentry/react"
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
  getName: () => string
  user: User | undefined
}

export function useUserManager(): UserManager {
  const settings = useQuery(api.getUserSettings, {
    key: "user-settings",
    params: [],
    onSuccess: (response) => {
      if (response.data?.email) {
        Sentry.setUser({ email: response.data.email })
      }
    },
  })

  const res = settings.result?.data
  const email = res?.email ?? ""
  const rights = res?.rights ?? []
  const requests = res?.requests ?? []

  function getRights(entityID: number) {
    return rights?.find((r) => r.entity.id === entityID) ?? null
  }

  function getName() {
    const firstRight = rights[0]
    return firstRight?.name ?? ""
  }

  function hasEntity(entityID: number) {
    return Boolean(getRights(entityID))
  }

  function hasEntities() {
    return rights.length > 0
  }

  function getFirstEntity() {
    return (rights[0]?.entity as Entity) ?? null
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
    getName,
    hasEntity,
    hasEntities,
    getFirstEntity,
    user: res,
  }
}

export const UserContext = createContext<UserManager | undefined>(undefined)

export function useUser() {
  const user = useContext(UserContext)
  if (user === undefined) throw new Error("User context is not defined")
  return user
}

export default useUserManager
