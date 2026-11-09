import { resolvePath, useLocation, useResolvedPath } from "react-router-dom"

export function useMatcher(basePath?: string) {
  const location = useLocation()
  const resolvedPath = useResolvedPath(".")
  const parentPath = (basePath ?? resolvedPath.pathname).trim()
  const currentPath = location.pathname.trim()

  return (path: string | undefined) => {
    if (path === undefined) {
      return null
    } else if (path.startsWith("#")) {
      return path === location.hash
    } else {
      const fromPath = /^\.\.(\/|$)/.test(path)
        ? resolvedPath.pathname
        : parentPath
      const tabPath = resolvePath(path, fromPath).pathname.trim()
      const startsWithPath =
        currentPath.startsWith(tabPath) &&
        currentPath.charAt(tabPath.length) === "/"
      return currentPath === tabPath || startsWithPath
    }
  }
}
