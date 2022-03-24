import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { Routes, Route } from "react-router-dom"
import { LoaderOverlay, Main, Title } from "common/components"
import Tabs from "common/components/tabs"
import useAPI from "common/hooks/use-api"
import { SettingsBody, SettingsHeader } from "settings/components/common"
import * as api from "./api"
import {
  EntityDoubleCountingList,
  EntityFactoriesList,
  EntityUsersList,
} from "./components/entity-list"
import EntityDetails from "./routes/entity-details"
import useTitle from "common-v2/hooks/title"
import Certificates from "./components/certificates"
import { SearchInput } from "common-v2/components/input"

const Entities = () => {
  const { t } = useTranslation()
  useTitle(t("Sociétés"))

  return (
    <Routes>
      <Route path=":id" element={<EntityDetails />} />
      <Route path="*" element={<EntityList />} />
    </Routes>
  )
}

const EntityList = () => {
  const { t } = useTranslation()
  const [query, setQuery] = useState<string | undefined>("")
  const [entities, getEntities] = useAPI(api.getEntities)
  const [tab, setTab] = useState("factories")

  useEffect(() => {
    getEntities(query ?? "")
  }, [getEntities, query])

  const entityTabs = [
    { key: "factories", label: t("Production / stockage") },
    { key: "doublecounting", label: t("Double comptage") },
    { key: "certificates", label: t("Certificats") },
    { key: "users", label: t("Utilisateurs") },
  ]

  const entityList = entities.data ?? []

  return (
    <Main>
      <SettingsHeader>
        <Title>Sociétés</Title>
      </SettingsHeader>

      <SettingsBody>
        <SearchInput
          clear
          debounce={250}
          label="Recherche"
          placeholder="Entrez du texte pour filtrer les résultats..."
          value={query}
          onChange={setQuery}
        />

        <Tabs tabs={entityTabs} focus={tab} onFocus={setTab} />

        {tab === "factories" && <EntityFactoriesList entities={entityList} />}

        {tab === "doublecounting" && (
          <EntityDoubleCountingList entities={entityList} />
        )}

        {tab === "certificates" && <Certificates search={query} />}

        {tab === "users" && <EntityUsersList entities={entityList} />}

        {entities.loading && <LoaderOverlay />}
      </SettingsBody>
    </Main>
  )
}

export default Entities
