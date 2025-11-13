import { resolvePath, useLocation, useResolvedPath } from "react-router-dom"

export function useMatcher() {
  const location = useLocation()
  const parentPath = useResolvedPath(".").pathname.trim()
  const currentPath = location.pathname.trim()

  return (path: string | undefined) => {
    if (path === undefined) {
      return null
    } else if (path.startsWith("#")) {
      return path === location.hash
    } else {
      const tabPath = resolvePath(path, parentPath).pathname.trim()
      const startsWithPath =
        currentPath.startsWith(tabPath) &&
        currentPath.charAt(tabPath.length) === "/"
      return currentPath === tabPath || startsWithPath
    }
  }
}
