import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import { Return } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import Tag from "common-v2/components/tag"
import { useTranslation } from "react-i18next"
import { LotScore } from "transaction-details/types"
import { Lot } from "transactions/types"
import css from "./score.module.css"

interface ScoreProps {
  lot: Lot
  big?: boolean
  details?: LotScore[]
}

export const Score = ({ lot, big, details }: ScoreProps) => {
  const portal = usePortal()

  if (!lot.data_reliability_score) return null
  const score = lot.data_reliability_score.toUpperCase() as keyof typeof colors

  return (
    <Tag
      big={big}
      label={score}
      className={css.scoreTag}
      style={{
        backgroundColor: colors[score],
        cursor: details ? "pointer" : undefined,
      }}
      onClick={() => {
        if (details) {
          portal((close) => (
            <ScoreDialog lot={lot} details={details} onClose={close} />
          ))
        }
      }}
    />
  )
}

interface ScoreDialogProps {
  lot: Lot
  details: LotScore[]
  onClose: () => void
}

const ScoreDialog = ({ lot, details, onClose }: ScoreDialogProps) => {
  const { t } = useTranslation()

  // prettier-ignore
  const scoreItems = {
    CUSTOMS_AND_CARBURE_MATCH: t("Les données de CarbuRe correspondent à celles des douanes"),
    DATA_SOURCE_IS_PRODUCER: t("La donnée a été entrée par le producteur du biocarburant"),
    LOT_DECLARED: t("Le lot a été validé au sein d'une déclaration"),
    PRODUCER_CERTIFICATE_EXISTS: t("Le certificat du producteur est connu par l'administration"),
    PRODUCER_CERTIFICATE_CHECKED: t("Le certificat du producteur a été validé par l'administration"),
    SUPPLIER_CERTIFICATE_EXISTS: t("Le certificat du fournisseur est connu par l'administration"),
    SUPPLIER_CERTIFICATE_CHECKED: t("Le certificat du fournisseur a été validé par l'administration"),
    FEEDSTOCK_REGISTERED: t("La matière première est bien déclarée sur le site de production"),
    BIOFUEL_REGISTERED: t("Le biocarburant est bien déclaré sur le site de production"),
    DELIVERY_SITE_REGISTERED: t("Le site de livraison est bien associé au client du lot"),
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Score de fiabilité de la donnée")}</h1>
      </header>
      <main>
        <section>
          <ul className={css.scoreList}>
            {details.map((detail) => (
              <li key={detail.item}>
                <div
                  className={css.scoreItem}
                  style={{
                    color:
                      detail.score > 0
                        ? detail.score === detail.max_score
                          ? "var(--green-dark)"
                          : "var(--blue-medium)"
                        : undefined,
                  }}
                >
                  <span>
                    {scoreItems[detail.item as keyof typeof scoreItems]}
                  </span>
                  <span className={css.separator} />
                  <span>
                    {detail.score} / {detail.max_score} {t("points")}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </section>
        <section>
          <div className={css.scoreResult}>
            <span>{t("Note obtenue")}</span>
            <span className={css.separator} />
            <Score big lot={lot} />
          </div>
        </section>
      </main>
      <footer>
        <Button asideX icon={Return} label={t("Retour")} action={onClose} />
      </footer>
    </Dialog>
  )
}

const colors = {
  A: "var(--score-a)",
  B: "var(--score-b)",
  C: "var(--score-c)",
  D: "var(--score-d)",
  E: "var(--score-e)",
  F: "var(--score-f)",
}

export default Score
