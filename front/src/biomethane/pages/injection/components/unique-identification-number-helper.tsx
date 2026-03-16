import { Dialog } from "common/components/dialog2"
import { NavLink } from "common/components/nav-link"
import { usePortal } from "common/components/portal"
import { Text } from "common/components/text"
import { useTranslation } from "react-i18next"

const UniqueIdentificationNumberDialog = ({
  onClose,
}: {
  onClose: () => void
}) => {
  return (
    <div>
      <Dialog
        onClose={onClose}
        header={
          <Dialog.Title>
            Numéro d'identifiant unique du site d'injection
          </Dialog.Title>
        }
      >
        <Text>
          Ce numéro correspond à votre numéro d'enregistrement dans le registre
          de capacité des gestionnaires de réseaux de gaz naturel. <br />
          <br />
          Il est accessible sur le site{" "}
          <NavLink
            target="_blank"
            to="https://odre.opendatasoft.com/explore/dataset/points-dinjection-de-biomethane-en-france/table/?disjunctive.site&disjunctive.nom_epci&disjunctive.departement&disjunctive.region&disjunctive.type_de_reseau&disjunctive.grx_demandeur&sort=capacite_de_production_gwh_an&disjunctive.augmentation_prevue&dataChart=eyJxdWVyaWVzIjpbeyJjaGFydHMiOlt7ImFsaWduTW9udGgiOnRydWUsInR5cGUiOiJjb2x1bW4iLCJmdW5jIjoiU1VNIiwieUF4aXMiOiJjYXBhY2l0ZV9kZV9wcm9kdWN0aW9uX2d3aF9hbiIsInNjaWVudGlmaWNEaXNwbGF5Ijp0cnVlLCJjb2xvciI6InJhbmdlLURhcmsyIn1dLCJ4QXhpcyI6InJlZ2lvbiIsIm1heHBvaW50cyI6bnVsbCwidGltZXNjYWxlIjoiIiwic29ydCI6IiIsInNlcmllc0JyZWFrZG93biI6InNpdGUiLCJzdGFja2VkIjoibm9ybWFsIiwiY29uZmlnIjp7ImRhdGFzZXQiOiJwb2ludHMtZGluamVjdGlvbi1kZS1iaW9tZXRoYW5lLWVuLWZyYW5jZSIsIm9wdGlvbnMiOnsiZGlzanVuY3RpdmUuc2l0ZSI6dHJ1ZSwiZGlzanVuY3RpdmUubm9tX2VwY2kiOnRydWUsImRpc2p1bmN0aXZlLmRlcGFydGVtZW50Ijp0cnVlLCJkaXNqdW5jdGl2ZS5yZWdpb24iOnRydWUsImRpc2p1bmN0aXZlLnR5cGVfZGVfcmVzZWF1Ijp0cnVlLCJkaXNqdW5jdGl2ZS5ncnhfZGVtYW5kZXVyIjp0cnVlLCJzb3J0IjoiLWRhdGVfZGVfbWVzIiwiZGlzanVuY3RpdmUuYXVnbWVudGF0aW9uX3ByZXZ1ZSI6dHJ1ZX19fV0sImRpc3BsYXlMZWdlbmQiOnRydWUsImFsaWduTW9udGgiOnRydWUsInRpbWVzY2FsZSI6IiJ9&disjunctive.ndeg_de_pitd_pitp&basemap=jawg.streets&location=6,47.26432,1.12061"
            underline
          >
            ODRé relatif aux points d'injection de biométhane
          </NavLink>
          . <br />
          <br />
          Le numéro à renseigner correspond au chiffre indiqué à la colonne "Id
          Unique Projet" et vous pouvez retrouver votre installation en
          réalisant un tri sur votre commune.
        </Text>
      </Dialog>
    </div>
  )
}

export const UniqueIdentificationNumberHelper = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  const handleClick = () => {
    portal((close) => <UniqueIdentificationNumberDialog onClose={close} />)
  }

  return (
    <button onClick={handleClick} style={{ padding: 0 }}>
      {t("Où trouver mon numéro ?")}
    </button>
  )
}
