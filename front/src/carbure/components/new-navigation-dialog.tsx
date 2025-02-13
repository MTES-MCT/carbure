import { Button } from "common/components/button2"
import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Text } from "common/components/text"
import { useState } from "react"
import { Trans } from "react-i18next"
import useLocalStorage from "common/hooks/storage"

export const NewNavigationDialog = () => {
  const [hasSeen, setHasSeen] = useLocalStorage(
    "carbure-new-navigation-dialog",
    false
  )
  const [open, setOpen] = useState(!hasSeen)

  const setHasSeenDialog = () => {
    setHasSeen(true)
    setOpen(false)
  }

  if (hasSeen || !open) return null

  return (
    <Portal>
      <Dialog
        onClose={setHasSeenDialog}
        fullWidth
        header={
          <Dialog.Title>
            <Trans>Nouvelle barre de navigation et formulaire de contact</Trans>
          </Dialog.Title>
        }
        footer={
          <Button onClick={setHasSeenDialog}>
            <Trans>Je découvre la nouvelle navigation</Trans>
          </Button>
        }
      >
        <Text>
          <Trans>
            CarbuRe se dote d'un nouveau système de navigation. Suite à un
            nombre croissant d'utilisateurs, ainsi que l'ajout de nouvelles
            filières d'énergies renouvelables (electricité, SAF) dans l'outil,
            nous avons repensé l'expérience de navigation pour faciliter votre
            usage au quotidien.
          </Trans>
        </Text>
        <br />
        <Text>
          <Trans>
            Nous passons désormais d'une barre de navigation latérale en haut ⬆️
            de la page à une barre de navigation latérale ⬅️ à gauche de
            l'outil.
          </Trans>
        </Text>
        <br />
        <Text>
          <Trans components={{ b: <b /> }}>
            <b>Comment changer d'entité ?</b> Rendez-vous en haut à gauche de la
            barre latérale de navigation, ouvrez le menu déroulant puis cliquez
            sur ajouter une entité.
          </Trans>
        </Text>
        <Text>
          <Trans components={{ b: <b /> }}>
            <b>Où sont mes paramètres ?</b> Ils sont désormais situés en bas à
            gauche de la page.
          </Trans>
        </Text>
        <Text>
          <Trans components={{ b: <b /> }}>
            <b>Vous avez besoin d'aide ?</b> Rendez-vous dans la rubrique Aide
            en haut à droite pour compléter notre formulaire de contact.
          </Trans>
        </Text>
        <Text>
          <Trans components={{ b: <b /> }}>
            <b>Où puis-je trouver mes statistiques et l'annuaire ?</b> Je clique
            sur mon compte en haut à droite.
          </Trans>
        </Text>
      </Dialog>
    </Portal>
  )
}
