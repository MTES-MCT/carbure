import React, { useEffect } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"

import styles from "./settings.module.css"

import * as common from "../../services/common"
import useAPI from "../../hooks/helpers/use-api"

import { Title, Box, Button } from "../system"
import { AlertCircle, Cross, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import Table, { Column, Row } from "../system/table"
import { ProductionSite } from "../../services/types"
import { SectionHeader, SectionBody, Section } from "../system/section"

const EMPTY_COLUMN = {
  className: styles.settingsTableEmptyColumn,
  render: () => null,
}

const PRODUCTION_SITE_COLUMNS: Column<ProductionSite>[] = [
  EMPTY_COLUMN,
  {
    header: "Nom",
    className: styles.settingsTableColumn,
    render: (ps) => <span>{ps.name}</span>,
  },
  {
    header: "Pays",
    className: styles.settingsTableColumn,
    render: (ps) => <span>{ps.country.name}</span>,
  },
  {
    header: "Date de mise en service",
    className: styles.settingsTableColumn,
    render: (ps) => <span>{ps.date_mise_en_service}</span>,
  },
]
type ProductionSitesSettingsProps = {
  entity: EntitySelection
}

const ProductionSitesSettings = ({ entity }: ProductionSitesSettingsProps) => {
  const [requestGetProductionSites, resolveGetProductionSites] = useAPI(common.findProductionSites); // prettier-ignore

  const entityID = entity?.id
  const productionSites = requestGetProductionSites.data ?? []
  const isEmpty = productionSites.length === 0

  const columns = [
    ...PRODUCTION_SITE_COLUMNS,
    {
      className: styles.settingsTableActionColumn,
      render: () => (
        <Box row className={styles.settingsTableActions}>
          <Cross title="Supprimer le site de production" />
        </Box>
      ),
    },
  ]

  const rows: Row<ProductionSite>[] = productionSites.map((ps) => ({ value: ps })); // prettier-ignore

  useEffect(() => {
    if (entityID) {
      resolveGetProductionSites("", entityID)
    }
  }, [entityID])

  return (
    <Section>
      <SectionHeader>
        <Title>Sites de production</Title>
        <Button level="primary" icon={Plus}>
          Ajouter un site de production
        </Button>
      </SectionHeader>

      {isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun site de production trouvé
          </Alert>
        </SectionBody>
      )}

      {!isEmpty && (
        <Table columns={columns} rows={rows} className={styles.settingsTable} />
      )}
    </Section>
  )
}

export default ProductionSitesSettings
