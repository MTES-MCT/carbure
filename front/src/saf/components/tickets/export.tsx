import Button from "common/components/button"
import { Download } from "common/components/icons"
import { useTranslation } from "react-i18next"
import { SafQuery } from "saf/types"

export interface ExportTicketsButtonProps {
  asideX?: boolean
  query: SafQuery
  getTickets: Function
}

export const ExportTicketsButton = ({
  asideX,
  query,
  getTickets,
}: ExportTicketsButtonProps) => {
  const { t } = useTranslation()
  return (
    <Button
      asideX={asideX}
      icon={Download}
      label={t("Exporter vers Excel")}
      action={() => getTickets(query)}
    />
  )
}
