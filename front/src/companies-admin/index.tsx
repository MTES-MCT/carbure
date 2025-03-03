import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Routes, Route } from "react-router-dom"
import EntityDetails from "./routes/entity-details"
import useTitle from "common/hooks/title"
import Certificates from "./components/certificates"
import { SearchInput } from "common/components/input"
import { EntitySummary } from "./components/entity-summary"
import { Main } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { Plus } from "common/components/icons"
import Button from "common/components/button"
import { usePortal } from "common/components/portal"
import AddEntityDialog from "./components/add-entity-dialog"
import { useNotify } from "common/components/notifications"
import { compact } from "common/utils/collection"
import useEntity from "common/hooks/entity"
import { usePrivateNavigation } from "common/layouts/navigation"
import { ExtAdminPagesEnum } from "api-schema"

const Entities = () => {
  const { t } = useTranslation()
  useTitle(t("Sociétés"))
  usePrivateNavigation(t("Sociétés"))

  return (
    <Routes>
      <Route path=":id" element={<EntityDetails />} />
      <Route path="*" element={<EntityList />} />
    </Routes>
  )
}

const EntityList = () => {
  const { t } = useTranslation()
  const [search, setSearch] = useState<string | undefined>("")
  const [tab, setTab] = useState("entities")
  const portal = usePortal()
  const notify = useNotify()
  const entity = useEntity()

  const isAdminDC = entity.isExternal && entity.hasAdminRight("DCA")
  const canAdd =
    entity.isExternal &&
    (entity.hasAdminRight(ExtAdminPagesEnum.AIRLINE) ||
      entity.hasAdminRight(ExtAdminPagesEnum.ELEC) ||
      entity.hasAdminRight(ExtAdminPagesEnum.DCA))

  const handleEntityAdded = (name: string) => {
    notify(
      t("La société {{name}} a bien été ajoutée.", {
        name,
      }),
      { variant: "success" }
    )
  }

  const showEntityDialog = () => {
    portal((close) => (
      <AddEntityDialog onClose={close} onEntityAdded={handleEntityAdded} />
    ))
  }

  return (
    <Main>
      <header>
        <section>
          <Tabs
            focus={tab}
            onFocus={setTab}
            variant="header"
            tabs={compact([
              { key: "entities", label: t("Récapitulatif") },
              (entity.isAdmin || isAdminDC) && {
                key: "certificates",
                label: t("Certificats"),
              },
            ])}
          />
          {canAdd && (
            <Button
              asideX
              variant="primary"
              icon={Plus}
              label={t("Ajouter une société")}
              action={showEntityDialog}
            />
          )}
        </section>
      </header>

      <section>
        <SearchInput
          clear
          debounce={250}
          label={t("Recherche")}
          placeholder={t("Entrez du texte pour filtrer les résultats...")}
          value={search}
          onChange={setSearch}
        />
        {tab === "entities" && <EntitySummary search={search} />}
        {(entity.isAdmin || isAdminDC) && tab === "certificates" && (
          <Certificates search={search} />
        )}
      </section>
    </Main>
  )
}

export default Entities
