import { Button } from "common/components/button2"
import { Table, Cell, Order } from "common/components/table2"
import { compact } from "common/utils/collection"
import { formatNumber, formatPeriod } from "common/utils/formatters"
import { memo, useMemo } from "react"
import { useTranslation } from "react-i18next"
import { To, useLocation, useNavigate } from "react-router-dom"
import { SafTicketSourcePreview, SafTicketSourceStatus } from "saf/types"
import { TicketSourceTag } from "./tag"
import { usePortal } from "common/components/portal"
import { useNotify } from "common/components/notifications"
import TicketsGroupedAssignment from "saf/components/assignment/grouped-assignment"
import { Text } from "common/components/text"
import { useSafRules } from "saf/hooks/useSafRules"

export interface TicketSourcesTableProps {
  loading: boolean
  ticketSources: SafTicketSourcePreview[]
  order: Order | undefined
  rowLink: (ticketSource: SafTicketSourcePreview) => To
  onOrder: (order: Order | undefined) => void
  selected: number[]
  onSelect: (selected: number[]) => void
  status: SafTicketSourceStatus
}

export const TicketSourcesTable = memo(
  ({
    loading,
    ticketSources,
    order,
    rowLink,
    onOrder,
    selected,
    onSelect,
    status,
  }: TicketSourcesTableProps) => {
    const columns = useColumns()
    const { t } = useTranslation()
    const portal = usePortal()
    const notify = useNotify()
    const { canUpdateTicket } = useSafRules()

    const selectedTicketSources = useMemo(() => {
      return ticketSources.filter((ticketSource) =>
        selected.includes(ticketSource.id)
      )
    }, [ticketSources, selected])

    const totalVolume = selectedTicketSources.reduce(
      (total, ticketSource) => total + ticketSource.total_volume,
      0
    )
    const assignedVolume = selectedTicketSources.reduce(
      (total, ticketSource) => total + ticketSource.assigned_volume,
      0
    )
    const remainingVolume = totalVolume - assignedVolume

    const handleTicketsAssigned = (
      volume: number,
      clientName: string,
      assignedTicketsCount: number
    ) => {
      notify(
        t(
          "{{volume}} litres ont bien été affectés à {{clientName}}. {{assignedTicketsCount}} tickets ont été générés.",
          {
            volume,
            clientName,
            assignedTicketsCount,
          }
        ),
        { variant: "success" }
      )
    }

    const showGroupedAssignement = () => {
      portal((close) => (
        <TicketsGroupedAssignment
          ticketSources={selectedTicketSources}
          remainingVolume={remainingVolume}
          onClose={close}
          onTicketsAssigned={handleTicketsAssigned}
        />
      ))
    }

    return (
      <Table
        loading={loading}
        order={order}
        onOrder={onOrder}
        rowLink={rowLink}
        rows={ticketSources}
        hasSelectionColumn={status === SafTicketSourceStatus.AVAILABLE}
        selectionText={t(
          "{{count}} volumes sélectionnés pour un total de {{remainingVolume}} L",
          {
            count: selectedTicketSources.length,
            remainingVolume: formatNumber(remainingVolume),
          }
        )}
        onSelect={onSelect}
        selected={selected}
        identify={(ticketSource) => ticketSource.id}
        columns={compact([
          columns.status,
          columns.availableVolume,
          columns.clients,
          columns.period,
          columns.feedstock,
          columns.ghgReduction,
          columns.parentLot,
        ])}
        topActions={[
          <Button
            priority="tertiary no outline"
            iconId="ri-send-plane-line"
            onClick={showGroupedAssignement}
            disabled={!canUpdateTicket}
            key="affect-volumes"
          >
            {t("Affecter les {{count}} volumes", {
              count: selectedTicketSources.length,
            })}
          </Button>,
        ]}
      />
    )
  }
)

export function useColumns() {
  const { t } = useTranslation()
  return {
    status: {
      header: t("Statut"),
      cell: (ticketSource: SafTicketSourcePreview) => (
        <TicketSourceTag ticketSource={ticketSource} />
      ),
    },

    availableVolume: {
      key: "volume",
      header: t("Volumes disponibles"),
      cell: (ticketSource: SafTicketSourcePreview) => (
        <Cell
          text={`${formatNumber(
            ticketSource.total_volume - ticketSource.assigned_volume
          )} L`}
          sub={`/${formatNumber(ticketSource.total_volume)} L`}
        />
      ),
    },

    clients: {
      // key: "clients",
      header: t("Clients"),
      cell: (ticketSource: SafTicketSourcePreview) => {
        const value =
          ticketSource.assigned_tickets.length > 0
            ? ticketSource.assigned_tickets.map((t) => t.client).join(", ")
            : "-"
        return <Cell text={value} />
      },
    },

    period: {
      key: "delivery",
      header: t("Période"),
      cell: (ticketSource: SafTicketSourcePreview) => {
        return (
          <Cell
            text={
              ticketSource.delivery_period
                ? formatPeriod(ticketSource.delivery_period)
                : t("N/A")
            }
          />
        )
      },
    },

    feedstock: {
      key: "feedstock",
      header: t("Matière première"),
      cell: (ticketSource: SafTicketSourcePreview) => (
        <Cell
          text={t(ticketSource.feedstock?.code ?? "", { ns: "feedstocks" })}
          sub={t(ticketSource.country_of_origin?.code_pays ?? "", {
            ns: "countries",
          })}
        />
      ),
    },

    ghgReduction: {
      small: true,
      key: "ghg_reduction",
      header: t("Réd. GES"),
      cell: (ticketSource: SafTicketSourcePreview) => {
        return (
          <Cell
            text={
              ticketSource.ghg_reduction
                ? `${ticketSource.ghg_reduction.toFixed(0)}%`
                : ""
            }
          />
        )
      },
    },

    parentLot: {
      key: "parent_lot",
      header: t("Lot parent"),
      cell: (ticketSource: SafTicketSourcePreview) => (
        <ParentLotButton lot={ticketSource.parent_lot} />
      ),
    },
  }
}

export default TicketSourcesTable

export interface ParentLotButtonProps {
  lot?: SafTicketSourcePreview["parent_lot"]
}

export const ParentLotButton = ({ lot }: ParentLotButtonProps) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()

  if (!lot) return <Cell text={t("N/A")} />

  const showLotDetails = () => {
    navigate({
      pathname: location.pathname,
      search: location.search,
      hash: `lot/${lot.id}`,
    })
  }

  return (
    <Cell
      text={
        <Button
          captive
          customPriority="link"
          title={t("Lot initial")}
          onClick={showLotDetails}
        >
          <Text size="sm" is="span">
            #{lot.carbure_id}
          </Text>
        </Button>
      }
      tooltipText={`#${lot.carbure_id}`}
    />
  )
}
