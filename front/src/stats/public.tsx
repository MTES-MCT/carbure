import { Route, Switch, Link } from "common/components/relative-route"
import { Main } from "common/components"
import IframeResizer from "iframe-resizer-react"
import Topbar from "./public-topbar"
import Footer from "carbure/components/footer"



const PublicStats = () => {
  return (
    <div>
      <Topbar />
      <Main style={{padding:"16px 160px"}}>
        <IframeResizer
          src="https://metabase.carbure.beta.gouv.fr/public/dashboard/98aaecc5-4899-4f6f-8649-fa906977e73b"
          frameBorder="0"
          allowTransparency
        />
      </Main>
      <Footer />
    </div>
  )
}

export default PublicStats