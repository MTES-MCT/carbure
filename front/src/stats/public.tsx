import { Route, Switch, Link } from "common/components/relative-route"
import { Main } from "common/components"
import { Section } from "common/components/section"
import IframeResizer from "iframe-resizer-react"
import Topbar from "./public-topbar"
import Footer from "carbure/components/footer"
import { Trans } from "react-i18next"


const PublicStats = () => {

  const publicLink = "https://metabase.carbure.beta.gouv.fr/public/dashboard/98aaecc5-4899-4f6f-8649-fa906977e73b"

  return (
    <div>
      <Topbar />
      <Main style={{padding:"16px 80px"}}>
        <Section style={{boxShadow: "1px 1px 4px grey"}}>
          <IframeResizer
            src = {publicLink}
            frameBorder="0"
            allowTransparency
          />
        </Section>
        <Section style={{backgroundColor:"#3150c0", alignSelf: "center", borderRadius: 15, width: "25%"}}>
          <h1 style={{alignSelf: "center"}}>
            <a href={publicLink} target="_blank" style={{color:"white"}}>
              <Trans>Lien des stats</Trans>
            </a>
          </h1>
        </Section>
      </Main>
      <Footer />
    </div>
  )
}

export default PublicStats