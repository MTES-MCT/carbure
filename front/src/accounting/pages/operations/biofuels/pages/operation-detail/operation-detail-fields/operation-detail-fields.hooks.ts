import { Operation, OperationType } from "accounting/types"
import { formatSector, formatTCO2Number } from "accounting/utils/formatters"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import {
  formatEnergyDisplay,
  formatQuantityDisplay,
} from "./operation-detail-fields.utils"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import { compact } from "common/utils/collection"
import useEntity from "common/hooks/entity"
import { ROUTE_URLS } from "common/utils/routes"
import { isCreditOperation } from "../../../operations.utils"

export const useOperationDetailFields = (operation?: Operation) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const exportationOrExpeditionFields =
    useExportationOrExpeditionFields(operation)

  return useMemo(() => {
    if (!operation) return []

    // Determine operation direction: positive quantity = receiving, negative = sending
    const isReceiver = (operation?.volume ?? 0) > 0
    const isSender = (operation?.volume ?? 0) < 0

    const applyRenewableShare = operation.renewable_energy_share !== 1
    const lotDetails = operation.details?.find((detail) => detail.lot !== null)
    const isGhgCorrection = operation.ghg_delta != null
    const transactionSign = isCreditOperation(operation.transaction) ? 1 : -1

    const lotHref = (lotId: number) => {
      const year = operation.year ?? new Date().getFullYear()
      const lotsUrl =
        entity.isAdmin || entity.isExternal || entity.isAuditor
          ? ROUTE_URLS.BIOFUELS_CONTROLS(entity.id, year).LOTS
          : ROUTE_URLS.BIOFUELS(entity.id, year).RECEIVED
      return `${lotsUrl}/history#lot/${lotId}`
    }

    // Define all possible conditional fields
    const fields = compact([
      { label: t("Filière"), value: formatSector(operation.sector) },
      {
        label: t("Date d'opération"),
        value: formatDate(operation?.created_at),
      },
      { label: t("Catégorie"), value: operation.customs_category },
      { label: t("Biocarburant"), value: operation.biofuel?.code },
      !isGhgCorrection && {
        label: t("Quantité"),
        value: formatQuantityDisplay(operation, applyRenewableShare),
      },
      !isGhgCorrection &&
        applyRenewableShare && {
          label: t("Energie renouvelable"),
          value: formatEnergyDisplay(operation),
        },
      !isGhgCorrection && {
        label: t("Tonnes CO2 eq évitées"),
        value: formatTCO2Number(
          (operation.corrected_avoided_emissions ??
            operation.avoided_emissions) * transactionSign
        ),
        originalValue:
          operation.corrected_avoided_emissions != null
            ? formatTCO2Number(operation.avoided_emissions * transactionSign)
            : undefined,
      },
      operation.ghg_delta != null && {
        label: t("Correction GES"),
        value: `${formatNumber(operation.ghg_delta, { signDisplay: "always" })} gCO₂/MJ`,
      },
      operation.type === OperationType.TRANSFERT &&
        isReceiver && {
          label: t("Expéditeur"),
          value: operation._entity ?? "-",
        },
      operation.type === OperationType.TRANSFERT &&
        isSender && {
          label: t("Destinataire"),
          value: operation._entity ?? "-",
        },
      ...exportationOrExpeditionFields,
      typeof operation.durability_period === "string" && {
        label:
          operation.type === OperationType.EXPIRATION
            ? t("Année de durabilité des volumes expirés")
            : t("Déclaration de durabilité"),
        value:
          operation.type === OperationType.EXPIRATION
            ? operation.durability_period
            : formatPeriod(operation.durability_period),
      },
      typeof operation.year === "number" && {
        label: t("Année"),
        value: operation.year,
      },
      operation.type === OperationType.TENEUR && {
        label: t("Objectif de filière IRICC"),
        value: formatSector(operation.objective_sector ?? operation.sector),
      },
      operation.type === OperationType.CORRECTION && lotDetails?.lot
        ? {
            label: t("Lot modifié n°"),
            value: t("{{id}}", { id: lotDetails.lot }),
            href: lotHref(lotDetails.lot),
          }
        : null,
      operation.type === OperationType.DEBT_REPAYMENT &&
        operation.debt && {
          label: t("Remboursement pour le lot n°"),
          value: operation.debt.lot.id,
          href: lotHref(operation.debt.lot.id),
        },
    ])

    return fields
  }, [entity, operation, t, exportationOrExpeditionFields])
}

const useExportationOrExpeditionFields = (operation?: Operation) => {
  const { t } = useTranslation()

  return useMemo(() => {
    const isExportationOrExpedition = [
      OperationType.EXPORTATION,
      OperationType.EXPEDITION,
    ].includes(operation?.type as OperationType)

    if (!operation || !isExportationOrExpedition) return []

    return [
      {
        label: t("Destinataire"),
        value: operation.export_recipient ?? "-",
      },
      {
        label: t("Dépôt expéditeur"),
        value: operation.from_depot ? operation.from_depot.name : "-",
      },
      operation.export_country && {
        label: t("Pays d'exportation"),
        value: operation.export_country ? operation.export_country.name : "-",
      },
    ]
  }, [operation, t])
}
