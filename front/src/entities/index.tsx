import { LoaderOverlay, Main, Title } from "common/components"
import { Alert, AlertFilter } from "common/components/alert"
import { AlertCircle, AlertTriangle } from "common/components/icons"
import { LabelInput } from "common/components/input"
import useAPI from "common/hooks/use-api"
import { useEffect, useState } from "react"
import { SettingsBody, SettingsHeader } from "settings/components/common"

import * as api from "./api"
import EntityList from "./components/entity-list"

const Entities = () => {
  const [query, setQuery] = useState("")
  const [requestOnly, setRequestOnly] = useState(false)
  const [entities, getEntities] = useAPI(api.getEntities)

  useEffect(() => {
    getEntities(query, requestOnly)
  }, [getEntities, query, requestOnly])

  const isEmpty = entities.data ? entities.data.length === 0 : true
  const requestCount = entities.data?.filter((e) => e.requests > 0).length ?? 0

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

        {isEmpty && (
          <Alert icon={AlertTriangle} level="warning">
            Aucune société trouvée pour cette recherche.
          </Alert>
        )}

        {requestCount > 0 && (
          <AlertFilter
            level="warning"
            icon={AlertCircle}
            active={requestOnly}
            onActivate={() => setRequestOnly(true)}
            onDispose={() => setRequestOnly(false)}
          >
            {requestCount === 1 ? (
              <span>
                <b>1 société</b> a des utilisateurs en attente d'autorisation.
              </span>
            ) : (
              <span>
                <b>{requestCount} sociétés</b> ont des utilisateurs en attente
                d'autorisation.
              </span>
            )}
          </AlertFilter>
        )}

        {!isEmpty && <EntityList entities={entities.data!} />}

        {entities.loading && <LoaderOverlay />}
      </SettingsBody>
    </Main>
  )
}

export default Entities
