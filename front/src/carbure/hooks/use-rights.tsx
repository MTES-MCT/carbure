import React, { useContext } from "react"
import { useParams } from "react-router-dom"

import { UserRight, UserRole } from "common/types"
import { AppHook } from "./use-app"

export type UserRightsSelection = UserRight | null

export const UserRightContext = React.createContext<UserRight | null>(null)

export function useRights() {
  const selected = useContext(UserRightContext)

  function is(role: UserRole) {
    return selected?.role === role
  }

  return { selected, is }
}

export function useRightSelection(app: AppHook): UserRightsSelection {
  const params: { entity: string } = useParams()
  const entityID = parseInt(params.entity, 10)

  return isNaN(entityID) ? null : app.getRights(entityID)
}

type UserRightProviderProps = {
  app: AppHook
  children: React.ReactNode
}

export const UserRightProvider = ({
  app,
  children,
}: UserRightProviderProps) => {
  const rights = useRightSelection(app)

  return (
    <UserRightContext.Provider value={rights}>
      {children}
    </UserRightContext.Provider>
  )
}
