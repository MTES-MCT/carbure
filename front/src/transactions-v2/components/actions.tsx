import { Fragment } from "react"
import Button from "common-v2/components/button"
import { ActionBar } from "common-v2/components/scaffold"
import { CreateButton, ExportButton } from "../actions"
import { AcceptButton } from "../actions/accept"
import { SendButton } from "../actions/send"
import { SearchInput } from "common-v2/components/input"
import { Cross, Flask, Wrench } from "common-v2/components/icons"
import { SubSwitcher } from "./switches"
import { LotQuery } from "../types"

export interface ActionBarProps {
  count: number
  query: LotQuery
  selection: number[]
  pending: number
  history: number
  sub: string
  search: string | undefined
  onSwitch: (tab: string) => void
  onSearch: (search: string | undefined) => void
}

export const Actions = ({
  count,
  sub,
  pending,
  history,
  search,
  onSwitch,
  onSearch,
  ...props
}: ActionBarProps) => {
  const { selection } = props
  const status = props.query.status ?? "UNKNOWN"
  const isEmpty = count === 0

  return (
    <ActionBar>
      {["IN", "OUT"].includes(status) && (
        <SubSwitcher
          sub={sub}
          pending={pending}
          history={history}
          onSwitch={onSwitch}
        />
      )}

      <ExportButton {...props} />

      {status === "DRAFT" && (
        <Fragment>
          <CreateButton />
          <SendButton {...props} disabled={isEmpty} />
          <Button
            disabled={isEmpty}
            variant="danger"
            icon={Cross}
            label={
              selection.length > 0 ? "Supprimer sélection" : "Supprimer tout"
            }
          />
        </Fragment>
      )}

      {status === "IN" && (
        <Fragment>
          <AcceptButton {...props} disabled={isEmpty} />
          <Button
            disabled={isEmpty}
            variant="danger"
            icon={Cross}
            label={selection.length > 0 ? "Refuser sélection" : "Refuser tout"}
          />
          <Button
            disabled={isEmpty || selection.length === 0}
            variant="warning"
            icon={Wrench}
            label={"Demander correction"}
          />
        </Fragment>
      )}

      {status === "STOCK" && (
        <Fragment>
          <Button variant="primary" icon={Flask} label={"Transformer"} />
        </Fragment>
      )}

      {status === "OUT" && (
        <Fragment>
          <Button label="TODO" />
        </Fragment>
      )}

      <SearchInput
        clear
        asideX
        debounce={240}
        value={search}
        onChange={onSearch}
      />
    </ActionBar>
  )
}
