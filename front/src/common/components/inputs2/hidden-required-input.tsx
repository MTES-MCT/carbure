const hiddenStyle: React.CSSProperties = {
  position: "absolute",
  bottom: 0,
  left: 0,
  width: 0,
  height: 0,
  opacity: 0,
  pointerEvents: "none",
}

export const HiddenRequiredInput = () => (
  <input //
    required
    type="text"
    value=""
    aria-hidden="true"
    style={hiddenStyle}
  />
)
