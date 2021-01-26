import useAPI from "common/hooks/use-api"
import { Main, Title } from "common/components"
import { SettingsBody, SettingsHeader } from "settings/components/common"

import * as api from "./api"
import { useEffect } from "react"
import Table from "common/components/table"
import { Entity } from "common/types"
import { empty } from "transactions/components/list-columns"

type RowData = { entity: Entity; declarations: api.DeclarationsByMonth }

const entityColumn = {
  render: (v: RowData) => v.entity.name,
}

function renderMonth(month: string) {
  return (v: RowData) => (
    <ul
      style={{
        margin: 0,
        padding: 8,
        fontWeight: "normal",
      }}
    >
      <li>{v.declarations[month]?.lots.num_drafts ?? 0} brouillons</li>
      <li>{v.declarations[month]?.lots.num_valid ?? 0} envoyés</li>
      <li>{v.declarations[month]?.lots.num_received ?? 0} reçus</li>
      <li>{v.declarations[month]?.lots.num_corrections ?? 0} corrections</li>
    </ul>
  )
}

const Dashboard = () => {
  const [declarations, getDeclarations] = useAPI(api.getDeclarations)

  useEffect(() => {
    getDeclarations()
  }, [getDeclarations])

  const [entities = [], months = [], declarationsByEntites = {}] =
    declarations.data ?? []

  const columns = months?.map((month) => ({
    header: month,
    render: renderMonth(month),
  }))

  const rows = entities?.map((e) => ({
    value: {
      entity: e,
      declarations: declarationsByEntites[e.id],
    } as RowData,
  }))

  return (
    <Main>
      <SettingsHeader>
        <Title>Tableau de bord</Title>
      </SettingsHeader>

      <SettingsBody>
        <Table columns={[empty, entityColumn, ...columns]} rows={rows} />
      </SettingsBody>
    </Main>
  )
}

export default Dashboard
