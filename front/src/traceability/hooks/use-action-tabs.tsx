import { Navigate, useLocation, useParams } from "react-router-dom"

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

  return {
    activeTab,
    hasTabs: (tabs?.length ?? 0) > 0,
    query: activeTab?.query,
    redirect,
    links,
  }
}

function tabPathname(
  pathname: string,
  tabKey: string | undefined,
  key: string
) {
  if (!tabKey) return `${pathname.replace(/\/$/, "")}/${key}`
  return pathname.replace(new RegExp(`/${tabKey}$`), `/${key}`)
}
