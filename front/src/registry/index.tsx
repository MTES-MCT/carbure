import { Main } from "common/components/scaffold"
import { Tabs } from "common/components/tabs"
import useTitle from "common/hooks/title"
import { useTranslation } from "react-i18next"
import Biofuels from "./components/biofuels"
import Companies from "./components/companies"
import Depots from "./components/depots"
import Feedstocks from "./components/feedstocks"
import DoubleCounting from "./components/double-counting"
import { usePrivateNavigation } from "common/layouts/navigation"
import { compact } from "common/utils/collection"
import { Airports } from "./components/airports"
import useEntity from "carbure/hooks/entity"

const Registry = () => {
  const { t } = useTranslation()
  const { isAirline, isOperator } = useEntity()

  useTitle(t("Annuaire"))
  usePrivateNavigation(t("Annuaire"))

  return (
    <Main>
      <Tabs
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
          (isAirline || isOperator) && {
            path: "#airports",
            key: "airports",
            label: t("Aéroports"),
          },
          {
            path: "#double-counting",
            key: "double-counting",
            label: t("Double comptage"),
          },
        ])}
      >
        {(focus) => (
          <section>
            {focus === "companies" && <Companies />}
            {focus === "feedstocks" && <Feedstocks />}
            {focus === "biofuels" && <Biofuels />}
            {focus === "depots" && <Depots />}
            {focus === "airports" && <Airports />}
            {focus === "double-counting" && <DoubleCounting />}
          </section>
        )}
      </Tabs>
    </Main>
  )
}

export default Registry
