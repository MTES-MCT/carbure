import { Overlay } from "common/components/scaffold"
import css from "./container.module.css"
import { Link } from "react-router-dom"
import marianne from "common/assets/images/Marianne.svg"
import { Title } from "common/components/title"

export const Container = ({ children }: { children: React.ReactNode }) => {
  return (
    <Overlay className={css.container}>
      <div className={css.content}>
        <header>
          <Link to="/" className={css.logo}>
            <img src={marianne} alt="marianne logo" />
            <Title is="h1" style={{ textAlign: "center" }}>
              CarbuRe
            </Title>
          </Link>
        </header>
        {children}
      </div>
    </Overlay>
  )
}
