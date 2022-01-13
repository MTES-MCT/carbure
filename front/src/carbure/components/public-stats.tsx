import { Main } from "common-v2/components/scaffold"
import IframeResizer from "iframe-resizer-react"

const PublicStats = () => {
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
