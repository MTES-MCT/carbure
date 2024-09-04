import { useEffect, useRef } from "react"

const useScrollToRef = (enabled?: boolean) => {
  const ref = useRef<HTMLElement>(null)

  useEffect(() => {
    if (ref?.current && enabled)
      ref.current.scrollIntoView({
        block: "end",
        behavior: "smooth",
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ref?.current, enabled])

  return {
    refToScroll: ref,
  }
}

export default useScrollToRef
