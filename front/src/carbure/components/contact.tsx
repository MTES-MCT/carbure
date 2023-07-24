import useTitle from "common/hooks/title"
import { Trans, useTranslation } from "react-i18next"
import styles from "./home.module.css"
import { Widget } from '@typeform/embed-react'


const Contact = () => {
  const { t } = useTranslation()
  useTitle(t("Accueil"))

  // const user = useUser()



  return (
    <main className={styles.home}>
      <section className={styles.homeTitle}>
        <h1><Trans>Contact</Trans></h1>
        <p>
          <Trans>Une question ? </Trans>
        </p>
      </section>
      <section >
        {/* Typeform API  https://www.typeform.com/developers/embed/react/ */}
        <Widget id="SgC1g8N7" style={{ width: '100%', height: "500px" }} className="my-form" />


      </section>

    </main>
  )
}

export default Contact
