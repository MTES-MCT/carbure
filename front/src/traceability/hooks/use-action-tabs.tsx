import { useRef } from "react"
import { Navigate, useLocation, useParams } from "react-router-dom"
import { equals } from "ramda"

import { ActionQuery } from "traceability/types"

export type ActionTab = {
  key: string
  label: string
  query?: Partial<ActionQuery>
}

export function useActionTabs(tabs?: ActionTab[]) {
  const { tab: tabKey } = useParams()
  const { pathname, search, hash } = useLocation()
  const activeTab = tabs?.find((tab) => tab.key === tabKey)

  const redirect =
    tabs?.length && !activeTab ? (
      <Navigate
        replace
        to={{
          pathname: tabPathname(pathname, tabKey, tabs[0]!.key),
          search,
          hash,
        }}
      />
    ) : null

  const links = tabs?.map((tab) => ({
    key: tab.key,
    label: tab.label,
    path: tabPathname(pathname, tabKey, tab.key),
  }))
  const query = useStableQuery(activeTab?.query)

  return {
    activeTab,
    hasTabs: (tabs?.length ?? 0) > 0,
    query,
    redirect,
    links,
  }
}

// Pages rebuild `tabs` on each render. Keep the previous query while its
// values stay the same, so the actions list does not refetch.
function useStableQuery(query: Partial<ActionQuery> | undefined) {
  const cache = useRef(query)
  if (!equals(cache.current, query)) {
    cache.current = query
  }
  return cache.current
}

function tabPathname(
  pathname: string,
  tabKey: string | undefined,
  key: string
) {
  if (!tabKey) return `${pathname.replace(/\/$/, "")}/${key}`
  return pathname.replace(new RegExp(`/${tabKey}$`), `/${key}`)
}
