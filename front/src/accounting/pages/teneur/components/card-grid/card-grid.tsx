import { Grid } from "common/components/scaffold"
import css from "./card-grid.module.css"

export const CardGrid = ({ children }: { children: React.ReactNode }) => {
  return <Grid className={css["card-grid"]}>{children}</Grid>
}
