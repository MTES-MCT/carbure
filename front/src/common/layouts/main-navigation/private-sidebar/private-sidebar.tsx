import styles from "./private-sidebar.module.css"

export const PrivateSidebar = () => {
  const a = Array.from({ length: 100 })

  return (
    <div className={styles["private-sidebar"]}>
      <div className={styles["nav-wrapper"]}>
        <div
          style={{ border: "1px solid red", padding: "20px 0", width: "100%" }}
        ></div>
        <nav>
          {a.map((_, index) => (
            <div key={index}>element {index}</div>
          ))}
        </nav>
      </div>

      <div className={styles["bottom-nav"]}>BOTTOM NAV</div>
    </div>
  )
}
