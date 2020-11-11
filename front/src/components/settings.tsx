import React, { useEffect, useState } from "react"
import { EntitySelection } from "../hooks/helpers/use-entity"
import { SettingsGetter } from "../hooks/use-app"

import styles from "./settings.module.css"

import * as api from "../services/settings"
import * as common from "../services/common"
import useAPI from "../hooks/helpers/use-api"

import {
  Section,
  BoxProps,
  Title,
  LabelCheckbox,
  LoaderOverlay,
  Box,
  Button,
  LabelInput,
} from "./system"

import { AlertCircle, Cross, Plus } from "./system/icons"
import { Alert } from "./system/alert"
import Table, { Column, Row } from "./system/table"
import { DeliverySite, ProductionSite } from "../services/types"

const EMPTY_COLUMN = {
  className: styles.settingsTableEmptyColumn,
  render: () => null,
}

function toggleMAC(toggle: boolean, entityID: number) {
  return toggle ? api.enableMAC(entityID) : api.disableMAC(entityID)
}

function toggleTrading(toggle: boolean, entityID: number) {
  return toggle ? api.enableTrading(entityID) : api.disableTrading(entityID)
}

export const SettingsHeader = (props: BoxProps) => (
  <Box className={styles.settingsTop}>
    <Box {...props} className={styles.settingsHeader} />
  </Box>
)

export const SettingsBody = (props: BoxProps) => (
  <Box {...props} className={styles.settingsBody} />
)

export const SectionHeader = (props: BoxProps) => (
  <Box {...props} row className={styles.settingsSectionHeader} />
)

export const SectionBody = (props: BoxProps) => (
  <Box {...props} className={styles.settingsSectionBody} />
)

export const SectionForm = (props: BoxProps) => (
  <Box {...props} as="form" className={styles.settingsSectionForm} />
)

type GeneralSettingsProps = {
  entity: EntitySelection
  settings: SettingsGetter
}

export const CompanySettings = ({ entity, settings }: GeneralSettingsProps) => {
  const isOperator = entity?.entity_type === "Opérateur"
  const isTrader = entity?.entity_type === "Trader"

  const hasMAC: boolean = entity?.has_mac ?? false
  const hasTrading: boolean = entity?.has_trading ?? false

  const [requestMAC, resolveToggleMAC] = useAPI(toggleMAC)
  const [requestTrading, resolveToggleTrading] = useAPI(toggleTrading)

  const isLoading =
    settings.loading || requestMAC.loading || requestTrading.loading

  function onChangeMac(e: React.ChangeEvent<HTMLInputElement>): void {
    if (entity !== null) {
      resolveToggleMAC(e.target.checked, entity.id).then(settings.resolve)
    }
  }

  function onChangeTrading(e: React.ChangeEvent<HTMLInputElement>): void {
    if (entity !== null) {
      resolveToggleTrading(e.target.checked, entity.id).then(settings.resolve)
    }
  }

  if (entity === null) {
    return null
  }

  return (
    <Section>
      <SectionHeader>
        <Title>Société</Title>
      </SectionHeader>

      <SectionBody>
        <LabelCheckbox
          disabled={isOperator}
          label="Ma société effectue des Mises à Consommation"
          checked={hasMAC || isOperator}
          onChange={onChangeMac}
          className={styles.settingsCheckbox}
        />

        <LabelCheckbox
          disabled={isOperator || isTrader}
          label="Ma société a une activité de négoce"
          checked={hasTrading || isTrader}
          onChange={onChangeTrading}
          className={styles.settingsCheckbox}
        />
      </SectionBody>

      {isLoading && <LoaderOverlay />}
    </Section>
  )
}

type ISCCCertificateSettingsProps = {
  entity: EntitySelection
}

export const ISCCCertificateSettings = ({
  entity,
}: ISCCCertificateSettingsProps) => {
  const [requestGetISCC, resolveGetISCC] = useAPI(api.getISCCTradingCertificates) // prettier-ignore

  const entityID = entity?.id
  const certificates = requestGetISCC.data ?? []
  const isEmpty = certificates.length === 0

  useEffect(() => {
    if (entityID) {
      resolveGetISCC(entityID)
    }
  }, [entityID])

  return (
    <Section>
      <SectionHeader>
        <Title>Certificats ISCC</Title>
        <Button level="primary" icon={Plus}>
          Ajouter un certificat ISCC
        </Button>
      </SectionHeader>

      {isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun certificat ISCC trouvé
          </Alert>
        </SectionBody>
      )}
    </Section>
  )
}

type BBSCertificateSettingsProps = {
  entity: EntitySelection
}

export const BBSCertificateSettings = ({
  entity,
}: BBSCertificateSettingsProps) => {
  const [requestGet2BS, resolveGet2BS] = useAPI(api.get2BSTradingCertificates) // prettier-ignore

  const entityID = entity?.id
  const certificates = requestGet2BS.data ?? []
  const isEmpty = certificates.length === 0

  useEffect(() => {
    if (entityID) {
      resolveGet2BS(entityID)
    }
  }, [entityID])

  return (
    <Section>
      <SectionHeader>
        <Title>Certificats 2BS</Title>
        <Button level="primary" icon={Plus}>
          Ajouter un certificat 2BS
        </Button>
      </SectionHeader>

      {isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun certificat 2BS trouvé
          </Alert>
        </SectionBody>
      )}
    </Section>
  )
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

export const ProductionSitesSettings = ({
  entity,
}: ProductionSitesSettingsProps) => {
  const [requestGetProductionSites, resolveGetProductionSites] = useAPI(common.findProductionSites) // prettier-ignore

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

  const rows: Row<ProductionSite>[] = productionSites.map((ps) => ({ value: ps })) // prettier-ignore

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

const DELIVERY_SITE_COLUMNS: Column<DeliverySite>[] = [
  EMPTY_COLUMN,
  {
    header: "N° douane",
    className: styles.settingsTableIDColumn,
    render: (ds) => <span>{ds.depot_id}</span>,
  },
  {
    header: "Nom",
    className: styles.settingsTableColumn,
    render: (ds) => <span>{ds.name}</span>,
  },
  {
    header: "Ville",
    className: styles.settingsTableColumn,
    render: (ds) => <span>{ds.city}</span>,
  },
  {
    header: "Pays",
    className: styles.settingsTableColumn,
    render: (ds) => <span>{ds.country.name}</span>,
  },
]

type DeliverySitesSettingsProps = {
  entity: EntitySelection
}

export const DeliverySitesSettings = ({
  entity,
}: DeliverySitesSettingsProps) => {
  const [query, setQuery] = useState("")
  const [requestGetDeliverySites, resolveGetDeliverySites] = useAPI(common.findDeliverySites) // prettier-ignore

  const entityID = entity?.id
  const deliverySites = requestGetDeliverySites.data ?? []
  const isEmpty = query.length === 0 || deliverySites.length === 0

  const rows: Row<DeliverySite>[] = deliverySites.map((ds) => ({ value: ds }))

  useEffect(() => {
    if (query) {
      resolveGetDeliverySites(query)
    }
  }, [query])

  return (
    <Section>
      <SectionHeader>
        <Title>Sites de livraison</Title>
        <Button level="primary" icon={Plus}>
          Ajouter un site de livraison
        </Button>
      </SectionHeader>

      <SectionForm>
        <LabelInput
          label="Vérifier l'existence d'un site de livraison"
          placeholder="Rechercher sur Carbure..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </SectionForm>

      {isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun site de livraison trouvé
          </Alert>
        </SectionBody>
      )}

      {!isEmpty && (
        <Table
          columns={DELIVERY_SITE_COLUMNS}
          rows={rows}
          className={styles.settingsTable}
        />
      )}
    </Section>
  )
}
