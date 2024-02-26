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
import DoubleCounting from "./components/double-counting"

const Registry = () => {
  const { t } = useTranslation()
  useTitle(t("Annuaire"))

  return (
    <Main>
      <header>
        <h1>
          <Trans>Annuaire CarbuRe</Trans>
        </h1>
      </header>

      <Tabs
        variant="sticky"
        tabs={[
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
          {
            path: "#depots",
            key: "depots",
            label: t("Dépôts"),
          },
          {
            path: "#double-counting",
            key: "double-counting",
            label: t("Double comptage"),
          },
        ]}
      >
        {(focus) => (
          <section>
            {focus === "companies" && <Companies />}
            {focus === "feedstocks" && <Feedstocks />}
            {focus === "biofuels" && <Biofuels />}
            {focus === "depots" && <Depots />}
            {focus === "double-counting" && <DoubleCounting />}
          </section>
        )}
      </Tabs>
    </Main>
  )
}

export default Registry
