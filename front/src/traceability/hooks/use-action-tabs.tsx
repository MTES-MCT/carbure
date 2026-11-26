import { Navigate, useLocation, useParams } from "react-router"

import { ActionQuery } from "traceability/types"
import { useStableQuery } from "traceability/hooks/use-stable-query"

export type ActionTab = {
  key: string
  label: string
  query?: Partial<ActionQuery>
}

const EMPTY_QUERY: Partial<ActionQuery> = {}

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
  const query = useStableQuery(activeTab?.query ?? EMPTY_QUERY)

  return {
    activeTab,
    hasTabs: (tabs?.length ?? 0) > 0,
    query,
    redirect,
    links,
  }
}

// Build the pathname of another tab by swapping the current tab segment.
// `tabKey` comes from useParams, which decodes it. `pathname` comes from
// useLocation and keeps the URL's own spelling: a typed "+" stays "+", while
// an already encoded "%2B" stays "%2B". These two hooks are not the same
// string. useMatch would return both from the decoded path, but it needs the
// full route pattern and this hook does not know the /org/:id prefix.
// useMatches would too, but it requires a data router and the app uses
// BrowserRouter. Compare both spellings as plain text.
function tabPathname(
  pathname: string,
  tabKey: string | undefined,
  key: string
) {
  const normalized = pathname.replace(/\/$/, "")
  if (!tabKey) return `${normalized}/${key}`

  const encoded = `/${encodeURIComponent(tabKey)}`
  const literal = `/${tabKey}`
  const suffix =
    encoded !== literal && normalized.endsWith(encoded) ? encoded : literal
  if (!normalized.endsWith(suffix)) return normalized
  return `${normalized.slice(0, -suffix.length)}/${key}`
}
