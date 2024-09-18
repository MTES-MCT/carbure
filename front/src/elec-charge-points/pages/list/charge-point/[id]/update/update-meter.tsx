import Dialog from "common/components/dialog"
import { PortalInstance } from "common/components/portal"

type UpdateMeterProps = {
  onClose: PortalInstance["close"]
}
export const UpdateMeter = ({ onClose }: UpdateMeterProps) => {
  return <Dialog onClose={onClose}>this is my dialog</Dialog>
}
