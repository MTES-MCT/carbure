import { Card } from "@codegouvfr/react-dsfr/Card"
import Tag from "@codegouvfr/react-dsfr/Tag"
import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"

interface AnnualDeclarationExportCardProps {
  year: number
  tagLabel?: string
  fileDescription?: string
  onDownload?: () => void
}

export const AnnualDeclarationExportCard = ({
  year,
  tagLabel,
  fileDescription,
  onDownload,
}: AnnualDeclarationExportCardProps) => {
  const { t } = useTranslation()
  const hasDownload = Boolean(fileDescription || onDownload)

  return (
    <Card
      title={year}
      start={
        <Tag style={{ marginBottom: "8px" }} small>
          {tagLabel ?? t("Déclarations annuelles")}
        </Tag>
      }
      endDetail={
        hasDownload ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              width: "100%",
            }}
          >
            {fileDescription && <span>{fileDescription}</span>}
            {onDownload && (
              <Button
                iconId="ri-download-line"
                title={t("Télécharger")}
                size="small"
                priority="tertiary no outline"
                asideX
                onClick={onDownload}
              />
            )}
          </div>
        ) : undefined
      }
    />
  )
}
