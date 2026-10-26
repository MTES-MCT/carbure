import {
  useLocation,
  useMatch,
  useParams,
  useResolvedPath,
} from "react-router-dom"

// Module tabs resolve from the base of their wildcard route, excluding `*`.
// An explicit pattern can still target a particular ancestor in redirect hooks.
export function useRouteBase(pattern?: string) {
  const match = useMatch(pattern ?? "/")
  const currentPath = useResolvedPath(".")
  const { pathname } = useLocation()
  const { "*": splat } = useParams()

  if (pattern) return match?.pathnameBase ?? currentPath.pathname
  if (!splat) return currentPath.pathname

  // Params are decoded, so find the matching suffix without changing the URL's
  // encoding or treating an encoded slash as an extra path segment.
  const segments = pathname.split("/")
  for (let index = 1; index < segments.length; index++) {
    try {
      const suffix = decodeURIComponent(
        segments.slice(index).join("/")
      ).replace(/%2F/g, "/")
      if (suffix === splat) return segments.slice(0, index).join("/") || "/"
    } catch {
      // Keep the router's resolved path for malformed percent encoding.
      return currentPath.pathname
    }
  }

  return currentPath.pathname
}
