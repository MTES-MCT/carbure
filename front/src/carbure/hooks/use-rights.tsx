import React, { useContext } from "react"
import { useMatch } from "react-router-dom"

import { UserRight, UserRole } from "common/types"
import { UserManager } from "./user"

export type UserRightsSelection = UserRight | null

export const UserRightContext = React.createContext<UserRight | null>(null)

export function useRights() {
  const selected = useContext(UserRightContext)

  function is(...roles: UserRole[]) {
    return selected ? roles.includes(selected.role) : false
  }

  return { selected, is }
}

export function useRightSelection(user: UserManager): UserRightsSelection {
  const match = useMatch<"entity">("/org/:entity/*")
  const entityID = parseInt(match?.params.entity ?? "", 10)
  return isNaN(entityID) ? null : user.getRights(entityID)
}

type UserRightProviderProps = {
  user: UserManager
  children: React.ReactNode
}

export const UserRightProvider = ({
  user,
  children,
}: UserRightProviderProps) => {
  const rights = useRightSelection(user)

  return (
    <UserRightContext.Provider value={rights}>
      {children}
    </UserRightContext.Provider>
  )
}
