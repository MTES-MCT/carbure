import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import { Box, Row } from "common/components/scaffold"
import { Title } from "common/components/title"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { getSnapshotBalance } from "accounting/pages/teneur/api"
import { useAnnualDeclarationTiruert } from "accounting/providers/annual-declaration-tiruert.provider"
import { SnapshotBalanceDialog } from "./snapshot-balance-dialog"

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
