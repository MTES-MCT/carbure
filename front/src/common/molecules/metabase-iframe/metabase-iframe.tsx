import IframeResizer from "@iframe-resizer/react"
import { useTranslation } from "react-i18next"
import { Notice } from "common/components/notice"
import { useQuery } from "common/hooks/async"
import { api } from "common/services/api-fetch"

type MetabaseIframeProps = {
  src: string
}

export const getMetabaseStatus = () =>
  api.GET("/metabase-status").then((res) => res.data)

export const MetabaseIframe = ({ src }: MetabaseIframeProps) => {
  const { t } = useTranslation()
  const { result, loading } = useQuery(getMetabaseStatus, {
    key: "metabase-status",
    params: [],
  })

  if (loading) return null

  if (!result?.available) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: 500,
        }}
      >
        <Notice
          variant="warning"
          title={t("Statistiques temporairement indisponibles")}
          style={{ maxWidth: 600, width: "100%" }}
        >
          <br />
          {t(
            "Ce service est temporairement indisponible pour cause de maintenance. Retour prévu dans quelques semaines. Merci de votre compréhension."
          )}
        </Notice>
      </div>
    )
  }

  return (
    <IframeResizer
      license="GPLv3"
      src={src}
      style={{ boxShadow: "var(--shadow)" }}
    />
  )
}
