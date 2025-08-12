export const getViewport = (
  name: string,
  dimensions: { width: string; height: string }
) => ({
  defaultViewport: name,
  viewports: {
    [name]: {
      name,
      styles: {
        width: dimensions.width,
        height: dimensions.height,
      },
    },
  },
})
