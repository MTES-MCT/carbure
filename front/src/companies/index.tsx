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

const Entities = () => {
  const { t } = useTranslation()
  useTitle(t("Sociétés"))

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
          <h1>Informations sur les sociétés</h1>
          <Button
            asideX
            variant="primary"
            icon={Plus}
            label={t("Ajouter une société")}
            action={showEntityDialog}
          />
        </section>
      </header>
      <Tabs
        focus={tab}
        onFocus={setTab}
        variant="sticky"
        tabs={[
          { key: "entities", label: t("Récapitulatif") },
          { key: "certificates", label: t("Certificats") },
        ]}
      />
      <section>
        <SearchInput
          clear
          debounce={250}
          label="Recherche"
          placeholder="Entrez du texte pour filtrer les résultats..."
          value={search}
          onChange={setSearch}
        />
        {tab === "entities" && <EntitySummary search={search} />}
        {tab === "certificates" && <Certificates search={search} />}
      </section>
    </Main>
  )
}

export default Entities
