import { Button } from "common/components/button2"
import { Collapse } from "common/components/collapse2"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { LotPreview } from "saf/types"

const ParentLot = ({ parent_lot }: { parent_lot?: LotPreview }) => {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()

  const showLotDetails = () => {
    navigate({
      pathname: location.pathname,
      search: location.search,
      hash: `lot/${parent_lot?.id}`,
    })
  }

  return (
    <Collapse label={t("Lot initial")} defaultExpanded>
      <section>
        <ul>
          <li>
            {parent_lot ? (
              <Button customPriority="link" onClick={showLotDetails}>
                {`${t("Lot")} #${parent_lot.carbure_id}`}
              </Button>
            ) : (
              t("Inconnu")
            )}
          </li>
        </ul>
      </section>
      <footer></footer>
    </Collapse>
  )
}

export default ParentLot
