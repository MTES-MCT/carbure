import React, {
  useEffect,
  useRef,
  useCallback,
  useState,
  createContext,
  useContext,
  useLayoutEffect,
} from "react"
import ReactDOM from "react-dom"

export interface PortalProps {
  children: React.ReactNode
  root?: HTMLElement
  onClose?: () => void
}

export const Portal = ({ children, root, onClose }: PortalProps) => {
  const portalRef = useRef<HTMLDivElement>(null)

  // when the portal closes, give focus back to the element that was active before the portal opened
  const activeRef = useRef(document.activeElement as HTMLElement | null)
  useLayoutEffect(() => () => activeRef.current?.focus(), [])

  // watch for interactions on the target to act as trigger
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      switch (e.key) {
        // when pressing escape close the portal if it's the last one opened
        case "Escape":
          if (isLastPortal(portalRef.current!)) onClose?.()
          break
      }
    }

    window.addEventListener("keydown", onKeyDown, true)
    return () => window.removeEventListener("keydown", onKeyDown, true)
  }, [onClose])

  // if the portal is opened in storybook, we need to render it in the storybook root
  // Couldn't find a better way to detect if we are in storybook
  const sbRoot = document.getElementById("storybook-root")

  return ReactDOM.createPortal(
    <div ref={portalRef} data-portal="">
      {children}
    </div>,
    root ?? sbRoot ?? document.body
  )
}

export function isLastPortal(element: Element) {
  return element.matches("[data-portal]:last-child")
}

export interface PortalProviderProps {
  children: React.ReactNode
}

export const PortalProvider = ({ children }: PortalProviderProps) => {
  const manager = usePortalManager()
  return (
    <PortalContext.Provider value={manager}>
      {children}
      {manager.portals.map((e) => (
        <Portal key={e.key} root={e.root} onClose={e.close}>
          {e.render(e.close)}
        </Portal>
      ))}
    </PortalContext.Provider>
  )
}

export interface PortalManager {
  portals: PortalInstance[]
  portal: PortalRegister
  close: (key: string) => void
  closeAll: () => void
}

export function usePortalManager(): PortalManager {
  const [portals, setPortals] = useState<PortalInstance[]>([])

  const closeKey = useCallback((key: string) => {
    setPortals((portals) => portals.filter((p) => p.key !== key))
  }, [])

  const portal = useCallback(
    (render: PortalRenderer, root?: HTMLElement) => {
      return new Promise<void>((resolve) => {
        const key = Math.random().toString(36).slice(2)
        function close() {
          closeKey(key)
          resolve()
        }
        setPortals((portals) => [...portals, { key, root, render, close }])
      })
    },
    [closeKey]
  )

  const closeAll = () => setPortals([])

  return { portals, portal, close: closeKey, closeAll }
}

export function usePortal(defaultRoot?: HTMLElement): PortalRegister {
  const manager = useContext(PortalContext)
  if (manager === undefined) throw new Error("Portal context is not defined")
  const portal = manager.portal
  return useCallback(
    (render, root = defaultRoot) => portal(render, root),
    [defaultRoot, portal]
  )
}

/**
 * To avoid refactor usePortal hook by exposing a closeAll function,
 * a new hook was created
 * @returns the closeAll portals function
 */
export function useCloseAllPortals(): PortalManager["closeAll"] {
  const manager = useContext(PortalContext)
  if (manager === undefined) throw new Error("Portal context is not defined")

  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useCallback(manager.closeAll, [manager.closeAll])
}

export const PortalContext = createContext<PortalManager | undefined>(undefined)

export type PortalRegister = (
  render: PortalRenderer,
  root?: HTMLElement
) => Promise<void>

export interface PortalInstance {
  key: string
  root?: HTMLElement
  render: PortalRenderer
  close: () => void
}

export type PortalRenderer = (close: () => void) => React.ReactElement<any, any>

export default Portal
