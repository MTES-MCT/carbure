import { createContext, useContext, useEffect } from "react"
import { useQuery } from "common/hooks/async-rq"
import { Entity, User, UserRight, UserRightRequest } from "common/types"
import * as api from "common/api"
import * as Sentry from "@sentry/react"

const userSettingsQueryKey = ["user-settings"] as const
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

  // Check if the user is admin of MTE - DGEC
  isMTEDGEC: boolean
}

export function useUserManager(): UserManager {
  const settings = useQuery({
    queryKey: userSettingsQueryKey,
    queryFn: api.getUserSettings,
  })

  const res = settings.data?.data
  const email = res?.email ?? ""
  const rights = res?.rights ?? []
  const requests = res?.requests ?? []

  useEffect(() => {
    if (res?.email) {
      Sentry.setUser({ email: res.email })
    }
  }, [res?.email])

  function getRights(entityID: number) {
    return rights?.find((r) => r.entity.id === entityID) ?? null
  }

  function getName() {
    return res?.name ?? ""
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
    return settings.data !== undefined && settings.error == null
  }

  return {
    loading: settings.isPending,
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
    isMTEDGEC: rights.some((right) => right.entity.name === "MTE - DGEC"),
  }
}

export const UserContext = createContext<UserManager | undefined>(undefined)

export function useUser() {
  const user = useContext(UserContext)
  if (user === undefined) throw new Error("User context is not defined")
  return user
}

export default useUserManager
