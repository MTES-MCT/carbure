import { Main } from "common/components"
import { Section } from "common/components/section"
import IframeResizer from "iframe-resizer-react"

const PublicStats = () => {
  const publicLink =
    "https://metabase.carbure.beta.gouv.fr/public/dashboard/98aaecc5-4899-4f6f-8649-fa906977e73b"

  return (
    <Main style={{ padding: "16px 80px" }}>
      <Section style={{ boxShadow: "1px 1px 4px grey" }}>
        <IframeResizer src={publicLink} frameBorder="0" allowTransparency />
      </Section>
    </Main>
  )
}

export default PublicStats
