import React, { useEffect } from "react"
import { useParams } from "react-router-dom"

import { UserRightRequest, UserRightStatus } from "common/types"

import * as api from "../api"
import useAPI from "common/hooks/use-api"
import useClose from "common/hooks/use-close"

import { Main, Title } from "common/components"
import { Section, SectionBody, SectionHeader } from "common/components/section"
import {
  formatDate,
  SettingsBody,
  SettingsHeader,
} from "settings/components/common"
import { Alert } from "common/components/alert"
import { Check, AlertTriangle, Cross, Return } from "common/components/icons"
import Table, { Actions, Column } from "common/components/table"
import { statusColumn } from "account/components/access-rights"
import { empty } from "transactions/components/list-columns"
import Sticky from "common/components/sticky"
import { Button } from "common/components/button"

const RIGHTS_COLUMNS: Column<UserRightRequest>[] = [
  empty,
  statusColumn,
  {
    header: "Utilisateur",
    render: (r) => r.user[0] ?? "",
  },
  {
    header: "Date",
    render: (r) => formatDate(r.date_requested),
  },
]

const RightsRequests = () => {
  const { id } = useParams<{ id: string }>()
  const [rightsRequests, getUsersRightRequests] = useAPI(
    api.getUsersRightRequests
  )

  useEffect(() => {
    getUsersRightRequests("", parseInt(id, 10), UserRightStatus.Pending)
  }, [getUsersRightRequests, id])

  const rows = (rightsRequests.data ?? []).map((r) => ({ value: r }))

  const actions = Actions([
    { title: "Accepter", icon: Check, action: () => console.log("accepted") },
    { title: "Refuser", icon: Cross, action: () => console.log("rejected") },
  ])

  return (
    <Section id="rights-requests">
      <SectionHeader>
        <Title>Demandes d'accès</Title>
      </SectionHeader>

      <SectionBody>
        {rows.length === 0 && (
          <Alert icon={Check} level="info">
            Aucune demande d'accès en cours pour cette société.
          </Alert>
        )}
      </SectionBody>

      {rows.length > 0 && (
        <Table columns={[...RIGHTS_COLUMNS, actions]} rows={rows} />
      )}
    </Section>
  )
}

const RightsGranted = () => {
  const { id } = useParams<{ id: string }>()
  const [rightsRequests, getUsersRightRequests] = useAPI(
    api.getUsersRightRequests
  )

  useEffect(() => {
    getUsersRightRequests("", parseInt(id, 10), UserRightStatus.Accepted)
  }, [getUsersRightRequests, id])

  const rows = (rightsRequests.data ?? []).map((r) => ({ value: r }))

  const actions = Actions([
    { title: "Révoqer", icon: Cross, action: () => console.log("revoked") },
  ])

  return (
    <Section id="rights-granted">
      <SectionHeader>
        <Title>Utilisateurs autorisés</Title>
      </SectionHeader>

      <SectionBody>
        {rows.length === 0 && (
          <Alert icon={AlertTriangle} level="info">
            Aucun utilisateur autorisé pour cette société
          </Alert>
        )}
      </SectionBody>

      {rows.length > 0 && (
        <Table columns={[...RIGHTS_COLUMNS, actions]} rows={rows} />
      )}
    </Section>
  )
}

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
        <a href="#rights-requests">Demandes d'accès</a>
        <a href="#rights-granted">Utilisateurs</a>
        <a href="#depots">Dépots</a>
        <a href="#production">Sites de production</a>
        <a href="#iscc">Certificats ISCC</a>
        <a href="#2bs">Certificats 2BS</a>
        <a href="#csn">Certificats système national</a>
      </Sticky>

      <SettingsBody>
        <RightsRequests />
        <RightsGranted />
      </SettingsBody>
    </Main>
  )
}

export default EntityDetails
