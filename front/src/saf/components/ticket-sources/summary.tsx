import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button from "common/components/button"
import { Filter } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { SafQuery } from "saf/types"
import * as api from "../../api"

export interface TicketSourcesSummaryProps {
  query: SafQuery
  selection: number[]
}

export const TicketSourcesSummary = ({
  query,
  selection,
}: TicketSourcesSummaryProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const summary = useQuery(api.getTicketSourcesSummary, {
    key: "lots-summary",
    params: [query, selection],
  })

  const summaryData = summary.result?.data.data ?? {
    count: 0,
    total_volume: 0,
  }

  const showGroupedAssignement = () => {
    //TODO Grouped assignement modal
    // portal((close) => (
    //   <TicketsGroupedAssignment
    //     ticketSources={}
    //     onClose={close}
    //     onTicketsAssigned={() => console.log('TODO')}
    //   />
    // ))
  }

  return (
    <Alert loading={summary.loading} icon={Filter} variant="info">
      <p>{t("3 volumes sélectionnés pour un total de 15 000 L")}</p>

      <Button
        asideX
        variant="primary"
        label={t("Affecter les 3 volumes")}
        action={showGroupedAssignement}
      />
    </Alert>
  )
}
