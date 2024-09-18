import Tag from "common/components/tag"
import { useTranslation } from "react-i18next"

type IsArticle2Props = {
  is_article_2: boolean
}
const IsArticle2 = ({ is_article_2 }: IsArticle2Props) => {
  const { t } = useTranslation()

  return (
    <Tag big variant={is_article_2 ? "none" : "info"}>
      {is_article_2 ? t("Pas concerné") : t("Concerné")}
    </Tag>
  )
}

export default IsArticle2
