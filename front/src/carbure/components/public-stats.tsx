import { Main } from "common-v2/components/scaffold"
import useTitle from "common-v2/hooks/title"
import IframeResizer from "iframe-resizer-react"
import { useTranslation } from "react-i18next"

const PublicStats = () => {
  const { t } = useTranslation()
  useTitle(t("Statistiques publiques"))

  const publicLink =
    "https://metabase.carbure.beta.gouv.fr/public/dashboard/98aaecc5-4899-4f6f-8649-fa906977e73b"

  return (
    <Main>
      <section>
        <IframeResizer
          src={publicLink}
          frameBorder="0"
          allowTransparency
          style={{ boxShadow: "var(--shadow)" }}
        />
      </section>
    </Main>
  )
}

export default PublicStats
