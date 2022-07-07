import { useTranslation } from "react-i18next"
import { Snapshot, Status } from "../types"
import { formatNumber } from "common/utils/formatters"
import Tabs from "common/components/tabs"
import { useMatch, useNavigate } from "react-router-dom"
import { useEffect } from "react"
import { compact } from "common/utils/collection"
import useEntity from "carbure/hooks/entity"

interface CategorySwitcherProps {
  category: string
  count: Snapshot["lots"] | undefined
  onSwitch: (category: string) => void
}

export const DraftsSwitcher = ({
  category,
  count,
  onSwitch,
}: CategorySwitcherProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  return (
    <Tabs
      keepSearch
      variant="switcher"
      focus={category}
      onFocus={onSwitch}
      tabs={compact([
        {
          key: "imported",
          path: "drafts/imported",
          label: `${t("Brouillons en attente")} (${formatNumber(count?.draft_imported ?? 0)})`, // prettier-ignore
        },
        entity.has_stocks && {
          key: "stocks",
          path: "drafts/stocks",
          label: `${t("Stocks prêts à l'envoi")} (${formatNumber(count?.draft_stocks ?? 0)})`, // prettier-ignore
        },
      ])}
    />
  )
}

export const InputSwitcher = ({
  category,
  count,
  onSwitch,
}: CategorySwitcherProps) => {
  const { t } = useTranslation()
  return (
    <Tabs
      keepSearch
      variant="switcher"
      focus={category}
      onFocus={onSwitch}
      tabs={[
        {
          key: "pending",
          path: "in/pending",
          label: `${t("En attente")} (${formatNumber(count?.in_pending ?? 0)})`, // prettier-ignore
        },
        {
          key: "correction",
          path: "in/correction",
          label: `${t("Corrections")} (${formatNumber(count?.in_tofix ?? 0)})`, // prettier-ignore
        },
        {
          key: "history",
          path: "in/history",
          label: `${t("Historique")} (${formatNumber(count?.in_total ?? 0)})`, // prettier-ignore
        },
      ]}
    />
  )
}

export const StockSwitcher = ({
  category,
  count,
  onSwitch,
}: CategorySwitcherProps) => {
  const { t } = useTranslation()
  return (
    <Tabs
      keepSearch
      variant="switcher"
      focus={category}
      onFocus={onSwitch}
      tabs={[
        {
          key: "pending",
          path: "pending",
          label: `${t("En stock")} (${formatNumber(count?.stock ?? 0)})`, // prettier-ignore
        },
        {
          key: "history",
          path: "history",
          label: `${t("Historique")} (${formatNumber(count?.stock_total ?? 0)})`, // prettier-ignore
        },
      ]}
    />
  )
}

export const OutputSwitcher = ({
  category,
  count,
  onSwitch,
}: CategorySwitcherProps) => {
  const { t } = useTranslation()

  return (
    <Tabs
      keepSearch
      variant="switcher"
      focus={category}
      onFocus={onSwitch}
      tabs={[
        {
          key: "pending",
          path: "out/pending",
          label: `${t("En attente")} (${formatNumber(count?.out_pending ?? 0)})`, // prettier-ignore
        },
        {
          key: "correction",
          path: "out/correction",
          label: `${t("Corrections")} (${formatNumber(count?.out_tofix ?? 0)})`, // prettier-ignore
        },
        {
          key: "history",
          path: "out/history",
          label: `${t("Historique")} (${formatNumber(count?.out_total ?? 0)})`, // prettier-ignore
        },
      ]}
    />
  )
}

export function useCategory() {
  const match = useMatch("/org/:entity/transactions/:year/:status/:category/*") // prettier-ignore
  return match?.params.category ?? "pending"
}

export function useAutoCategory(
  status: Status,
  snapshot: Snapshot | undefined
) {
  const navigate = useNavigate()
  const match = useMatch("/org/:entity/transactions/:year/:status/:category/*") // prettier-ignore
  const category = match?.params.category

  useEffect(() => {
    const defaultCategory = getDefaultCategory(status, snapshot)
    if (!isStatusCategory(status, category)) {
      if (status === "stocks") navigate(defaultCategory, { replace: true })
      else navigate(`${status}/${defaultCategory}`, { replace: true })
    }
  }, [category, status, snapshot, navigate])

  return category ?? getDefaultCategory(status, snapshot)
}

export function getDefaultCategory(
  status: string,
  snapshot: Snapshot | undefined
) {
  if (snapshot === undefined) return "pending"

  if (status === "drafts") {
    if (snapshot.lots.draft_imported > 0) return "imported"
    else if (snapshot.lots.draft_stocks > 0) return "stocks"
    else return "imported"
  }

  const count = snapshot.lots

  let pending = 0
  let tofix = 0
  let total = 0

  if (status === "in") {
    pending = count.in_pending
    tofix = count.in_tofix
    total = count.in_total
  } else if (status === "out") {
    pending = count.out_pending
    tofix = count.out_tofix
    total = count.out_total
  } else if (status === "stocks") {
    pending = count.stock
    total = count.stock_total
  }

  if (pending > 0) return "pending"
  else if (tofix > 0) return "correction"
  else if (total > 0) return "history"
  else return "pending"
}

function isStatusCategory(status: string, category: string | undefined) {
  if (category === undefined) {
    return false
  } else if (status === "drafts") {
    return ["imported", "stocks"].includes(category)
  } else if (status === "stocks") {
    return ["pending", "history"].includes(category)
  } else {
    return ["pending", "correction", "history"].includes(category)
  }
}
