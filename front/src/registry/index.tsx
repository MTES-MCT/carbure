import { Main } from "common/components/scaffold"
import { Tabs } from "common/components/tabs"
import useTitle from "common/hooks/title"
import { compact } from "common/utils/collection"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import Biofuels from "./components/biofuels"
import Companies from "./components/companies"
import Depots from "./components/depots"
import Feedstocks from "./components/feedstocks"

const Registry = () => {
  const { t } = useTranslation()
  useTitle(t("Annuaire"))
  const [focus, setFocus] = useState("companies")

  return (
    <Main>
      <header>
        <h1>
          <Trans>Annuaire CarbuRe</Trans>
        </h1>
      </header>

      <Tabs
        focus={focus}
        onFocus={setFocus}
        variant="sticky"
        tabs={compact([
          {
            path: "#companies",
            key: "companies",
            label: t("Sociétés"),
          },
          {
            path: "#feedstocks",
            key: "feedstocks",
            label: t("Matières premières"),
          },
          {
            path: "#biofuels",
            key: "biofuels",
            label: t("Biocarburants"),
          },
          {
            path: "#depots",
            key: "depots",
            label: t("Dépôts"),
          },
        ])}
      />

      <section>
        {focus === "companies" && <Companies />}
        {focus === "feedstocks" && <Feedstocks />}
        {focus === "biofuels" && <Biofuels />}
        {focus === "depots" && <Depots />}
      </section>
    </Main>
  )
}

export default Registry
