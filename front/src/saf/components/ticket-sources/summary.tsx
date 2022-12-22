import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import Button from "common/components/button"
import { Filter } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { useQuery } from "common/hooks/async"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { SafQuery, SafTicketSource } from "saf/types"
import * as api from "../../api"
import TicketsGroupedAssignment from "../assignment/grouped-assignment"

export interface TicketSourcesSummaryProps {
  ticketSources: SafTicketSource[]
}

export const TicketSourcesSummary = ({
  ticketSources,
}: TicketSourcesSummaryProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  console.log("ticketSources:", ticketSources)
  // const summary = useQuery(api.getTicketSourcesSummary, {
  //   key: "lots-summary",
  //   params: [query, selection],
  // })

  // const summaryData = summary.result?.data.data ?? {
  //   count: 0,
  //   total_volume: 0,
  // }

  const totalVolume = ticketSources.reduce(
    (total, ticketSource) => total + ticketSource.total_volume,
    0
  )

  const assignedVolume = ticketSources.reduce(
    (total, ticketSource) => total + ticketSource.assigned_volume,
    0
  )
  console.log("assignedVolume:", assignedVolume)

  const remainingVolume = totalVolume - assignedVolume

  console.log("totalVolume:", totalVolume)

  const showGroupedAssignement = () => {
    //TODO Grouped assignement modal
    portal((close) => (
      <TicketsGroupedAssignment
        ticketSources={ticketSources}
        remainingVolume={remainingVolume}
        onClose={close}
        onTicketsAssigned={() => console.log("TODO")}
      />
    ))
  }

  return (
    <Alert icon={Filter} variant="info">
      <p>
        {t(
          "{{volumeCount}} volumes sélectionnés pour un total de {{remainingVolume}} L",
          {
            volumeCount: ticketSources.length,
            remainingVolume: formatNumber(remainingVolume),
          }
        )}
      </p>

      <Button
        asideX
        variant="primary"
        label={t("Affecter les {{volumeCount}} volumes", {
          volumeCount: ticketSources.length,
        })}
        action={showGroupedAssignement}
      />
    </Alert>
  )
}
