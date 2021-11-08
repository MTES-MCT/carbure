import { createContext, useContext } from 'react'
import { useAsync } from 'react-async-hook'
import { Entity, Settings, UserRight, UserRightRequest } from 'common/types'
import { api, Api } from 'common-v2/api'
import { useInvalidate } from 'common-v2/hooks/invalidate'


export interface User {
  loading: boolean
  email: string | undefined
  rights: UserRight[]
  requests: UserRightRequest[]
  reload: () => void
  isAuthenticated: () => boolean
  getRights: (entityID: number) => UserRight | null
  hasEntity: (entityID: number) => boolean
  hasEntities: () => boolean
  getFirstEntity: () => Entity | null
}

export function useUser(): User {
  const settings = useAsync(() => api.get<Api<Settings>>('v3/settings'), [])
  const reload = useInvalidate('user-settings', settings.execute)

  const res = settings.result?.data.data
  const email = res?.email
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
    return settings.error?.message !== "User not verified"
  }

  return {
    loading: settings.loading,
    email,
    rights,
    requests,
    reload,
    isAuthenticated,
    getRights,
    hasEntity,
    hasEntities,
    getFirstEntity,
  }
}

export const UserContext = createContext<User | undefined>(undefined)

export function useUserContext() {
  const user = useContext(UserContext)
  if (user === undefined) throw new Error('User context is not defined')
  return user
}

export default useUser