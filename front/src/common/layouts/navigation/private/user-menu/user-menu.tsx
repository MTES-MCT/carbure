import { useUser } from "carbure/hooks/user"
import { SimpleMenu } from "common/components/menu2"
import { Text } from "common/components/text"
import css from "./user-menu.module.css"
export const UserMenu = () => {
  const { user } = useUser()

  const name = "John Doe"

  return (
    <SimpleMenu
      iconId="fr-icon-arrow-down-s-line"
      iconPosition="right"
      priority="tertiary"
      size="small"
      label={name}
    >
      <div className={css["user-menu-infos"]}>
        <Text size="sm" fontWeight="bold">
          John Doe
        </Text>
        <Text size="sm" fontWeight="regular">
          {user?.email}
        </Text>
      </div>
    </SimpleMenu>
  )
}
