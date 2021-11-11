import { Fragment } from "react"
import Button from "common-v2/components/button"
import { ActionBar } from "common-v2/components/scaffold"
import { CreateButton, ExportButton } from "../actions"
import { AcceptButton } from "../actions/accept"
import { SendButton } from "../actions/send"
import { LotQuery } from "../types"
import { SearchInput } from "common-v2/components/input"

export interface ActionBarProps {
  count: number
  query: LotQuery
  selection: number[]
  search: string | undefined
  onSearch: (search: string | undefined) => void
}

export const Actions = ({
  count,
  search,
  onSearch,
  ...props
}: ActionBarProps) => {
  const status = props.query.status
  const isEmpty = count === 0

  return (
    <ActionBar>
      <ExportButton {...props} />

      {status === "DRAFT" && (
        <Fragment>
          <CreateButton />
          <SendButton {...props} disabled={isEmpty} />
        </Fragment>
      )}

      {status === "IN" && (
        <Fragment>
          <AcceptButton {...props} disabled={isEmpty} />
        </Fragment>
      )}

      {status === "STOCK" && (
        <Fragment>
          <Button label="TODO" />
        </Fragment>
      )}

      {status === "OUT" && (
        <Fragment>
          <Button label="TODO" />
        </Fragment>
      )}

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
