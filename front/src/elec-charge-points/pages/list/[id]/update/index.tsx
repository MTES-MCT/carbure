import Dialog from "common/components/dialog"
import Portal from "common/components/portal"
import { useLocation, useNavigate } from "react-router-dom"

export const UpdateChargePointDialog = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const closeDialog = () => navigate({ search: location.search, hash: "#" })

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          Tag
          <h1>title</h1>
        </header>

        <main>
          <section>content</section>
        </main>
      </Dialog>
    </Portal>
  )
}
