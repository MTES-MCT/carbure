import { LoaderOverlay, Main, Title } from "common/components"
import { Alert } from "common/components/alert"
import { AlertTriangle } from "common/components/icons"
import { LabelInput } from "common/components/input"
import Tabs from "common/components/tabs"
import useAPI from "common/hooks/use-api"
import { Fragment, useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { SettingsBody, SettingsHeader } from "settings/components/common"

import * as api from "./api"
import {
  EntityCertificatesList,
  EntityDoubleCountingList,
  EntityFactoriesList,
  EntityUsersList,
} from "./components/entity-list"

const Entities = () => {
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

  const isEmpty = entities.data ? entities.data.length === 0 : true

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

        {isEmpty && (
          <Alert icon={AlertTriangle} level="warning">
            Aucune société trouvée pour cette recherche.
          </Alert>
        )}

        {!isEmpty && (
          <Fragment>
            {tab === "factories" && (
              <EntityFactoriesList entities={entities.data!} />
            )}

            {tab === "doublecounting" && (
              <EntityDoubleCountingList entities={entities.data!} />
            )}

            {tab === "certificates" && (
              <EntityCertificatesList entities={entities.data!} />
            )}

            {tab === "users" && <EntityUsersList entities={entities.data!} />}
          </Fragment>
        )}

        {entities.loading && <LoaderOverlay />}
      </SettingsBody>
    </Main>
  )
}

export default Entities
