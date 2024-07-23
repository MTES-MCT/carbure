import cl from "clsx"
import Button from "common/components/button"
import Dialog from "common/components/dialog"

import { Check, Cross, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import Tag from "common/components/tag"
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

// - customs and carbure match (4pts)
// - data source is producer (3pts)
// - lot declared (1pt)
// - certificates validated by admin (2pts)
//   -- producer_certificate_checked (1pt)
//   -- supplier_certificate_checked (1pt)
// - configuration anomalies (1pt)
//   -- feedstock_registered [ ]
//   -- biofuel_registered [ ]
//   -- delivery_site_registered [ ]
// - certificate anomalies (1pt)
//   -- producer_certificate_provided [ ]
//   -- producer_certificate_exists [ ]
//   -- supplier_certificate_provided [ ]
//   -- supplier_certificate_exists [ ]

const ScoreDialog = ({ lot, details, onClose }: ScoreDialogProps) => {
  const { t } = useTranslation()

  // prettier-ignore
  const scoreItems = {
    CUSTOMS_AND_CARBURE_MATCH: t("Les données de CarbuRe correspondent à celles des douanes"), // 0 or 4 --- NO META
    DATA_SOURCE_IS_PRODUCER: t("La donnée a été entrée par le producteur du biocarburant"), // 0 or 3 --- NO META
    LOT_DECLARED: t("Le lot a été validé au sein d'une déclaration"), // 0 or 1 --- NO META
    CERTIFICATES_VALIDATED: t("Les certificats ont été approuvés par l'administration"), // 0, 1, 2 --- META
    ANOMALIES_CONFIGURATION: t("Les sites de production et de livraison sont bien configurés"), // 0, 1 ---META
    ANOMALIES_CERTIFICATES: t("Les certificats ne présentent aucune anomalie"), // 0, 1 --- META
  }

  const scoreSubItems = {
    producer_certificate_checked: t(
      "Le certificat du producteur a été approuvé par l'administration"
    ),
    supplier_certificate_checked: t(
      "Le certificat du fournisseur a été approuvé par l'administration"
    ),
    producer_certificate_provided: t(
      "Le certificat du producteur est bien renseigné"
    ),
    producer_certificate_exists: t(
      "Le certificat du producteur existe dans la base de données CarbuRe"
    ),
    supplier_certificate_provided: t(
      "Le certificat du fournisseur est bien renseigné"
    ),
    supplier_certificate_exists: t(
      "Le certificat du fournisseur existe dans la base de données CarbuRe"
    ),
    feedstock_registered: t(
      "La matière première est bien déclarée sur le site de production"
    ),
    biofuel_registered: t(
      "Le biocarburant est bien déclaré sur le site de production"
    ),
    delivery_site_registered: t(
      "Le site de livraison est bien associé au client du lot"
    ),
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
                    {detail.score} / {detail.max_score}{" "}
                    {t("points", { count: detail.max_score })}
                  </span>
                </div>
                {detail.meta && (
                  <ul className={css.scoreSubItems}>
                    {Object.entries(detail.meta).map(([meta, checked]) => (
                      <li
                        key={meta}
                        className={cl(css.scoreSubItem)}
                        style={{
                          color: !checked ? "var(--gray-dark)" : undefined,
                        }}
                      >
                        <span>
                          {scoreSubItems[meta as keyof typeof scoreSubItems]}
                        </span>
                        <span className={css.separator} />
                        {checked ? (
                          <Check
                            size={20}
                            color="var(--green-dark)"
                            style={{ border: "1px solid var(--green-dark)" }}
                          />
                        ) : (
                          <Cross
                            size={20}
                            color="var(--red-dark)"
                            style={{ border: "1px solid var(--red-dark)" }}
                          />
                        )}
                      </li>
                    ))}
                  </ul>
                )}
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
