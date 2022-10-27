import { useEffect, useRef } from "react"

const useScrollToRef = (enabled?: boolean) => {
  const ref = useRef<HTMLElement>(null)
  console.log('ref:', ref)

  useEffect(() => {
    if (ref?.current && enabled)
      ref.current.scrollIntoView({
        block: "end",
        behavior: "smooth",
      })
  }, [ref?.current, enabled])

  return {
    refToScroll: ref,
  }
}


export default useScrollToRef