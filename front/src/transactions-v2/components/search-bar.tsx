import { useEffect } from "react"
import { useTranslation } from "react-i18next"
import { Snapshot } from "../types"
import { formatNumber } from "common-v2/utils/formatters"
import { useStatus } from "./status"
import { SearchInput } from "common-v2/components/input"
import { ActionBar } from "common-v2/components/scaffold"
import Tabs from "common-v2/components/tabs"

export interface SearchBarProps {
  category: string
  search: string | undefined
  count: Snapshot["lots"] | undefined
  onSearch: (search: string | undefined) => void
  onSwitch: (category: string) => void
}

export const SearchBar = ({ search, onSearch, ...props }: SearchBarProps) => {
  const status = useStatus()
  const { onSwitch } = props

  useEffect(() => {
    onSwitch("pending")
  }, [status, onSwitch])

  return (
    <ActionBar>
      {status === "drafts" && <DraftsSwitcher {...props} />}
      {status === "in" && <InputSwitcher {...props} />}
      {status === "stocks" && <StockSwitcher {...props} />}
      {status === "out" && <OutputSwitcher {...props} />}

      <SearchInput
        asideX
        clear
        debounce={240}
        value={search}
        onChange={onSearch}
      />
    </ActionBar>
  )
}

interface CategorySwitcherProps {
  category: string
  count: Snapshot["lots"] | undefined
  onSwitch: (category: string) => void
}

const DraftsSwitcher = ({
  category,
  count,
  onSwitch,
}: CategorySwitcherProps) => {
  const { t } = useTranslation()
  return (
    <Tabs
      variant="switcher"
      focus={category}
      onFocus={onSwitch}
      tabs={[
        {
          key: "pending",
          label: `${t("Tous les brouillons")} (${formatNumber(count?.draft ?? 0)})`, // prettier-ignore
        },
      ]}
    />
  )
}

const InputSwitcher = ({
  category,
  count,
  onSwitch,
}: CategorySwitcherProps) => {
  const { t } = useTranslation()
  return (
    <Tabs
      variant="switcher"
      focus={category}
      onFocus={onSwitch}
      tabs={[
        {
          key: "pending",
          label: `${t("En attente")} (${formatNumber(count?.in_pending ?? 0)})`, // prettier-ignore
        },
        {
          key: "correction",
          label: `${t("Corrections")} (${formatNumber(count?.in_tofix ?? 0)})`, // prettier-ignore
        },
        {
          key: "history",
          label: `${t("Historique")} (${formatNumber(count?.in_total ?? 0)})`, // prettier-ignore
        },
      ]}
    />
  )
}

const StockSwitcher = ({
  category,
  count,
  onSwitch,
}: CategorySwitcherProps) => {
  const { t } = useTranslation()
  return (
    <Tabs
      variant="switcher"
      focus={category}
      onFocus={onSwitch}
      tabs={[
        {
          key: "pending",
          label: `${t("En stock")} (${formatNumber(count?.stock ?? 0)})`, // prettier-ignore
        },
        {
          key: "history",
          label: `${t("Historique")} (${formatNumber(count?.stock_total ?? 0)})`, // prettier-ignore
        },
      ]}
    />
  )
}

const OutputSwitcher = ({
  category,
  count,
  onSwitch,
}: CategorySwitcherProps) => {
  const { t } = useTranslation()
  return (
    <Tabs
      variant="switcher"
      focus={category}
      onFocus={onSwitch}
      tabs={[
        {
          key: "pending",
          label: `${t("En attente")} (${formatNumber(count?.out_pending ?? 0)})`, // prettier-ignore
        },
        {
          key: "correction",
          label: `${t("Corrections")} (${formatNumber(count?.out_tofix ?? 0)})`, // prettier-ignore
        },
        {
          key: "history",
          label: `${t("Historique")} (${formatNumber(count?.out_total ?? 0)})`, // prettier-ignore
        },
      ]}
    />
  )
}

export default SearchBar
