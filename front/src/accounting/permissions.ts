import { EntityManager } from "common/hooks/entity"
import { ExternalAdminPages } from "common/types"

export interface AccountingPermissions {
  canAccessModule: boolean
  canAccessBalances: boolean

  /** Redevable routes operations/* and balances/* — not for admin profiles */
  canAccessOperations: boolean
  canAccessObjectives: boolean
  canAccessTeneur: boolean

  adminPermissions: {
    canAccessAdmin: boolean
    canAccessObjectives: boolean
    canAccessOperations: boolean
  }

  canAccessElecSector: boolean
  canTransferBalance: boolean
  canUpdateBiofuelOperation: boolean
  canUpdateElecOperation: boolean
}

export const hasAccise = (entity: EntityManager) => entity.accise_number !== ""

export const isLiable = (entity: EntityManager) => entity.is_tiruert_liable

export const isDGDDINationalAdmin = (entity: EntityManager) =>
  entity.isExternal && entity.hasAdminRight(ExternalAdminPages.DGDDI_NATIONAL)

export const canAccessAdmin = (entity: EntityManager) =>
  entity.isAdmin || isDGDDINationalAdmin(entity)

const canAccessElecSector = (entity: EntityManager) =>
  (entity.isOperator && entity.has_elec) ||
  entity.isAdmin ||
  entity.hasAdminRight(ExternalAdminPages.ELEC)

const deniedPermissions = (): AccountingPermissions => ({
  canAccessModule: false,
  canAccessBalances: false,
  canAccessOperations: false,
  canAccessObjectives: false,
  canAccessTeneur: false,
  adminPermissions: {
    canAccessAdmin: false,
    canAccessObjectives: false,
    canAccessOperations: false,
  },
  canAccessElecSector: false,
  canTransferBalance: false,
  canUpdateBiofuelOperation: false,
  canUpdateElecOperation: false,
})

export const getAccountingPermissions = (
  entity: EntityManager,
  isAuthenticated: boolean
): AccountingPermissions => {
  if (!isAuthenticated) return deniedPermissions()

  const admin = canAccessAdmin(entity)
  const canAccessModule = hasAccise(entity) || admin
  const canAccessObjectives = isLiable(entity) || admin
  const canWrite = entity.canWrite()

  return {
    canAccessModule,
    canAccessBalances: canAccessModule && !admin,
    canAccessOperations: canAccessModule && !admin,
    canAccessObjectives,
    canAccessTeneur: isLiable(entity) && !admin,
    adminPermissions: {
      canAccessAdmin: admin,
      canAccessObjectives: admin,
      canAccessOperations: admin,
    },
    canAccessElecSector: canAccessElecSector(entity),
    canTransferBalance: canWrite,
    canUpdateBiofuelOperation: canWrite,
    canUpdateElecOperation: canWrite,
  }
}
