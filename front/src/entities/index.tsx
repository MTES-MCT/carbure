import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { Routes, Route } from "react-router-dom"
import { LoaderOverlay, Main, Title } from "common/components"
import { LabelInput } from "common/components/input"
import Tabs from "common/components/tabs"
import useAPI from "common/hooks/use-api"
import { SettingsBody, SettingsHeader } from "settings/components/common"
import * as api from "./api"
import {
  EntityCertificatesList,
  EntityDoubleCountingList,
  EntityFactoriesList,
  EntityUsersList,
} from "./components/entity-list"
import EntityDetails from "./routes/entity-details"

const Entities = () => {
  return (
    <Routes>
      <Route path=":id" element={<EntityDetails />} />
      <Route path="*" element={<EntityList />} />
    </Routes>
  )
}

const EntityList = () => {
  const { t } = useTranslation()
  const [query, setQuery] = useState("")
  const [entities, getEntities] = useAPI(api.getEntities)
  const [tab, setTab] = useState("factories")

  useEffect(() => {
    getEntities(query)
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
        <LabelInput
          label="Rechercher..."
          placeholder="Entrez le nom d'une société..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        <Tabs tabs={entityTabs} focus={tab} onFocus={setTab} />

        {tab === "factories" && <EntityFactoriesList entities={entityList} />}

        {tab === "doublecounting" && (
          <EntityDoubleCountingList entities={entityList} />
        )}

        {tab === "certificates" && (
          <EntityCertificatesList entities={entityList} />
        )}

        {tab === "users" && <EntityUsersList entities={entityList} />}

        {entities.loading && <LoaderOverlay />}
      </SettingsBody>
    </Main>
  )
}

export default Entities
