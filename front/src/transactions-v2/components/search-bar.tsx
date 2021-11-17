import { useTranslation } from "react-i18next"
import { Snapshot } from "../types"
import useStatus from "../hooks/status"
import { SearchInput } from "common-v2/components/input"
import { ActionBar } from "common-v2/components/scaffold"
import Tabs from "common-v2/components/tabs"
import { useEffect } from "react"

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
          label: `${t("Tous les brouillons")} (${count?.draft ?? 0})`,
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
          label: `${t("En attente")} (${count?.in_pending ?? 0})`,
        },
        {
          key: "correction",
          label: `${t("En correction")} (${count?.in_tofix ?? 0})`,
        },
        {
          key: "history",
          label: `${t("Historique")} (${count?.in_total ?? 0})`,
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
          label: `${t("En stock")} (${count?.stock ?? 0})`,
        },
        {
          key: "history",
          label: `${t("Historique")} (${count?.stock_total ?? 0})`,
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
          label: `${t("En attente")} (${count?.out_pending ?? 0})`,
        },
        {
          key: "correction",
          label: `${t("À corriger")} (${count?.out_tofix ?? 0})`,
        },
        {
          key: "history",
          label: `${t("Historique")} (${count?.out_total ?? 0})`,
        },
      ]}
    />
  )
}
