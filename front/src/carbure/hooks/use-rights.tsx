import React, { useContext } from "react"
import { useMatch } from "react-router-dom"

import { UserRight, UserRole } from "common/types"
import { AppHook } from "./use-app"

export type UserRightsSelection = UserRight | null

export const UserRightContext = React.createContext<UserRight | null>(null)

export function useRights() {
  const selected = useContext(UserRightContext)

  function is(...roles: UserRole[]) {
    return selected ? roles.includes(selected.role) : false
  }

  return { selected, is }
}

export function useRightSelection(app: AppHook): UserRightsSelection {
  const match = useMatch<"entity">('/org/:entity/*')
  const entityID = parseInt(match?.params.entity ?? '', 10)

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
