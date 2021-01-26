import React, { useEffect } from "react"
import { useParams } from "react-router-dom"

import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"

import { Main, Title } from "common/components"
import { Return } from "common/components/icons"
import Sticky from "common/components/sticky"
import { Button } from "common/components/button"
import { SettingsBody, SettingsHeader } from "settings/components/common"
import UserRights from "../components/user-rights"
import * as api from "../api"

const EntityDetails = () => {
  const close = useClose("..")
  const { id } = useParams<{ id: string }>()
  const [entity, getEntity] = useAPI(api.getEntityDetails)

  useEffect(() => {
    getEntity(parseInt(id, 10))
  }, [getEntity, id])

  return (
    <Main>
      <SettingsHeader row>
        <Title>{entity.data?.name}</Title>
        <Button icon={Return} onClick={close}>
          Retour
        </Button>
      </SettingsHeader>

      <Sticky>
        <a href="#users">Utilisateurs</a>
        <a href="#depots">Dépots</a>
        <a href="#production">Sites de production</a>
        <a href="#iscc">Certificats ISCC</a>
        <a href="#2bs">Certificats 2BS</a>
        <a href="#csn">Certificats système national</a>
      </Sticky>

      <SettingsBody>
        <UserRights />
      </SettingsBody>
    </Main>
  )
}

export default EntityDetails
