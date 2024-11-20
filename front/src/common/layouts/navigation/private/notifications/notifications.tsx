import { SimpleMenu } from "common/components/menu2"

export const Notifications = () => {
  return (
    <SimpleMenu
      buttonProps={{
        priority: "tertiary",
        iconId: "ri-notification-3-line",
        size: "small",
        title: "Notifications",
      }}
      dropdownWidth="300px"
    >
      My menu
    </SimpleMenu>
  )
}
