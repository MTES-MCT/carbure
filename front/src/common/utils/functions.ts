export function debounce<F extends (...args: any[]) => any>(
  fn: F,
  waitMs: number
): (...args: Parameters<F>) => Promise<Awaited<ReturnType<F>>> {
  let timer: ReturnType<typeof setTimeout> | null = null
  let lastArgs: Parameters<F>
  let pendingReject: ((reason?: any) => void) | null = null

  return ((...args: Parameters<F>) => {
    lastArgs = args

    if (timer) {
      clearTimeout(timer)
      pendingReject?.(new Error("Debounced"))
    }

    return new Promise<ReturnType<F>>((resolve, reject) => {
      pendingReject = reject

      timer = setTimeout(() => {
        timer = null
        pendingReject = null

        try {
          // Call the function; if it returns a promise, wait on it
          const result = fn(...lastArgs)
          Promise.resolve(result).then(resolve, reject)
        } catch (err) {
          reject(err)
        }
      }, waitMs)
    })
  }) as F
}
