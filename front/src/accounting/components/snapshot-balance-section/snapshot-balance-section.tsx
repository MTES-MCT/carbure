import { useState } from "react"
import { useTranslation } from "react-i18next"
import { apiTypes } from "common/services/api-fetch.types"
import { Button } from "common/components/button2"
import Dialog from "common/components/dialog2/dialog"
import { Portal, usePortal } from "common/components/portal"
import { Box, Row } from "common/components/scaffold"
import { Table } from "common/components/table2"
import { Title } from "common/components/title"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { formatNumber } from "common/utils/formatters"
import { getSnapshotBalance } from "accounting/pages/teneur/api"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { formatSector } from "accounting/utils/formatters"
import { Notice } from "common/components/notice"
import css from "./snapshot-balance-section.module.css"

type BalanceEntry = apiTypes["SnapshotBalanceEntry"]

export const SnapshotBalanceSection = ({ entityId }: { entityId?: number }) => {
  const entity = useEntity()
  const { t } = useTranslation()
  const portal = usePortal()
  const { selectedYear, currentDeclarationYear } = useAnnualDeclarationTiruert()
  const isCurrent = selectedYear === currentDeclarationYear
  const snapshotYear = isCurrent ? selectedYear - 1 : selectedYear

  const { result } = useQuery(getSnapshotBalance, {
    key: `snapshot-balance-${entity.id}-${entityId ?? entity.id}-${snapshotYear}`,
    params: [entity.id, snapshotYear, entityId],
  })

  if (!result) return null

  const title = isCurrent
    ? t("Reliquats {{year}}", { year: snapshotYear })
    : t("Soldes reportés en {{year}}", { year: snapshotYear + 1 })

  return (
    <Box>
      <Row>
        <Title is="h1" as="h3">
          {title}
        </Title>
        <Button
          asideX
          priority="secondary"
          iconId="fr-icon-eye-line"
          onClick={() =>
            portal((close) => (
              <SnapshotBalanceDialog
                title={title}
                entries={result.results}
                onClose={close}
              />
            ))
          }
        >
          {isCurrent ? t("Voir les reliquats") : t("Voir les soldes reportés")}
        </Button>
      </Row>
    </Box>
  )
}

const SnapshotBalanceDialog = ({
  title,
  entries,
  onClose,
}: {
  title: string
  entries: BalanceEntry[]
  onClose: () => void
}) => {
  const { t } = useTranslation()
  const [page, setPage] = useState(1)
  const pageSize = 7
  const pageCount = Math.ceil(entries.length / pageSize)
  const columns = [
    {
      header: t("Filière"),
      cell: (row: BalanceEntry) => formatSector(row.sector),
    },
    {
      header: t("Biocarburant"),
      cell: (row: BalanceEntry) => row.biofuel ?? "-",
    },
    {
      header: t("Catégorie"),
      cell: (row: BalanceEntry) => row.customs_category ?? "-",
    },
    {
      header: t("Quantité (L/GJ)"),
      cell: (row: BalanceEntry) => (
        <>
          {formatNumber(row.volume)} L
          <br />
          <span style={{ color: "var(--text-mention-grey)" }}>
            {formatNumber(row.energy / 1000)} GJ
          </span>
        </>
      ),
    },
    {
      header: t("tCO2 évitées"),
      cell: (row: BalanceEntry) => formatNumber(row.saved_emissions),
    },
  ]

  return (
    <Portal>
      <Dialog
        fullWidth
        onClose={onClose}
        header={<Dialog.Title>{title}</Dialog.Title>}
      >
        {entries.length === 0 && (
          <Notice noColor variant="info">
            {t("Aucun solde disponible pour cette année.")}
          </Notice>
        )}
        <div style={{ maxHeight: 470, overflow: "auto" }}>
          {entries.length > 0 && (
            <Table
              className={css.table}
              columns={columns}
              rows={entries.slice((page - 1) * pageSize, page * pageSize)}
            />
          )}
        </div>
        {pageCount > 1 && (
          <Row style={{ justifyContent: "center", alignItems: "center" }}>
            <Button
              priority="tertiary no outline"
              iconId="fr-icon-arrow-left-s-line"
              title={t("Précédent")}
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            />
            <span>
              {page} / {pageCount}
            </span>
            <Button
              priority="tertiary no outline"
              iconId="fr-icon-arrow-right-s-line"
              title={t("Suivant")}
              disabled={page === pageCount}
              onClick={() => setPage(page + 1)}
            />
          </Row>
        )}
      </Dialog>
    </Portal>
  )
}
