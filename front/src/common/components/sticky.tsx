import cl from "clsx"
import React, { useEffect, useRef, useState } from "react"
import styles from "./sticky.module.css"

function getPosition(element: HTMLElement): number {
  const prev = element.previousElementSibling
  const rect = prev?.getBoundingClientRect()
  return rect ? rect.bottom : 0
}

const Sticky = ({ children }: { children: React.ReactNode }) => {
  const [sticky, setSticky] = useState(false)
  const div = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = document.getElementById("root")!

    function onScroll(e: Event) {
      if (!div.current) return

      const scrollY = container.scrollTop
      const posY = getPosition(div.current) + scrollY

      if (scrollY >= posY) {
        setSticky(true)
      } else if (sticky && scrollY <= posY) {
        setSticky(false)
      }
    }

    container.addEventListener("scroll", onScroll)
    return () => container.removeEventListener("scroll", onScroll)
  })

  return (
    <React.Fragment>
      {/* keep the previous space occupied when getting fixed position  */}
      {sticky && <div style={{ height: 56 }} />}
      <div
        ref={div}
        className={cl(styles.sticky, sticky && styles.stickyFixed)}
      >
        {children}
      </div>
    </React.Fragment>
  )
}

export default Sticky
