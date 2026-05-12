import { useEffect, useRef, useState } from "react"

export const usePulseAnimation = (trigger: unknown, duration = 300) => {
  const [animate, setAnimate] = useState(false)
  const isFirstRenderRef = useRef(true)

  useEffect(() => {
    if (isFirstRenderRef.current) {
      isFirstRenderRef.current = false
      return
    }

    setAnimate(true)
    const timeout = globalThis.setTimeout(() => setAnimate(false), duration)
    return () => globalThis.clearTimeout(timeout)
  }, [duration, trigger])

  return animate
}
