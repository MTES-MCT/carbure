import { EntityManager } from "common/hooks/entity"
import { ExternalAdminPages } from "common/types"

export interface AccountingPermissions {
  canAccessModule: boolean
  canAccessBalances: boolean

  /** Liable routes operations/* and balances/* — not for admin profiles */
  canAccessOperations: boolean

  liable: {
    canAccessObjectives: boolean
  }

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

export const isLiable = (entity: EntityManager) => entity.is_tiruert_liable

/** Mirrors backend can_access_balance_and_operations (web/tiruert/permissions.py). */
export const canAccessBalanceAndOperations = (entity: EntityManager) =>
  entity.isOperator ||
  ((entity.isTrader || entity.isProducer) && entity.has_mac)

/** Mirrors backend can_access_objectives (web/tiruert/permissions.py). */
export const canAccessLiableObjectives = (entity: EntityManager) =>
  canAccessBalanceAndOperations(entity) && isLiable(entity)

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
  liable: {
    canAccessObjectives: false,
  },
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
  const canAccessBalanceAndOps = canAccessBalanceAndOperations(entity)
  const canAccessModule = admin || canAccessBalanceAndOps
  const canWrite = entity.canWrite()

  return {
    canAccessModule,
    canAccessBalances: canAccessBalanceAndOps && !admin,
    canAccessOperations: canAccessBalanceAndOps && !admin,
    liable: {
      canAccessObjectives: canAccessLiableObjectives(entity) && !admin,
    },
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
