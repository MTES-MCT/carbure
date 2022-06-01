import React, {
  useEffect,
  useRef,
  useCallback,
  useState,
  createContext,
  cloneElement,
  useContext,
} from "react"
import ReactDOM from "react-dom"

export interface PortalProps {
  children: React.ReactNode
  onClose?: () => void
}

export const Portal = ({ children, onClose }: PortalProps) => {
  const containerRef = useRef(document.createElement("div"))

  // add the container div to the document and remove it when not needed
  useEffect(() => {
    const portal = containerRef.current
    ;(portal.dataset as any).portal = true
    document.body.appendChild(portal)
    return () => portal.remove()
  }, [])

  // watch for interactions on the target to act as trigger
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      switch (e.key) {
        // when pressing escape close the portal if it's the last one opened
        case "Escape":
          if (isLastPortal(containerRef.current)) onClose?.()
          break
      }
    }

    window.addEventListener("keydown", onKeyDown, true)
    return () => window.removeEventListener("keydown", onKeyDown, true)
  }, [onClose])

  return ReactDOM.createPortal(children, containerRef.current)
}

export function isLastPortal(element: Element) {
  return element.matches("div[data-portal]:last-child")
}

export interface PortalProviderProps {
  children: React.ReactNode
}

export const PortalProvider = ({ children }: PortalProviderProps) => {
  const manager = usePortalManager()
  return (
    <PortalContext.Provider value={manager}>
      {children}
      <Portals list={manager.portals} />
    </PortalContext.Provider>
  )
}

export type PortalRenderer = (close: () => void) => React.ReactElement<any, any>

export interface PortalManager {
  portals: PortalInstance[]
  portal: (render: PortalRenderer) => Promise<void>
  close: (key: string) => void
}

export function usePortalManager(): PortalManager {
  const [portals, setPortals] = useState<PortalInstance[]>([])

  const closeKey = useCallback((key: string) => {
    setPortals((portals) => portals.filter((p) => p.key !== key))
  }, [])

  const portal = useCallback(
    (render: PortalRenderer) =>
      new Promise<void>((resolve) => {
        const key = Math.random().toString(36).slice(2)
        function close() {
          closeKey(key)
          resolve()
        }
        const content = render(close)
        setPortals((portals) => [...portals, { key, content, close }])
      }),
    [closeKey]
  )

  return { portals, portal, close: closeKey }
}

export function usePortal() {
  const manager = useContext(PortalContext)
  if (manager === undefined) throw new Error("Portal context is not defined")
  return manager.portal
}

export const PortalContext = createContext<PortalManager | undefined>(undefined)

export interface PortalsProps {
  list: PortalInstance[]
}

export const Portals = ({ list }: PortalsProps) => {
  if (list.length === 0) return null
  else return <>{list.map((e) => cloneElement(e.content, { key: e.key }))}</>
}

export interface PortalInstance {
  key: string
  content: React.ReactElement<any, any>
  close: () => void
}

export default Portal
