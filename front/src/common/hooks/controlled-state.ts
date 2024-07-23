import { useCallback, useEffect, useRef, useState } from "react"

export function useControlledState<T>(
	initialState: T,
	stateControlled: T | undefined,
	setStateControlled: ((state: T) => void) | undefined
): [T, (state: T) => void] {
	const initialStateRef = useRef(initialState)
	const defaultState = initialStateRef.current

	const [state, _setState] = useState(stateControlled ?? defaultState)

	useEffect(() => {
		_setState(stateControlled ?? defaultState)
	}, [stateControlled, defaultState])

	const setState = useCallback(
		(nextState: T) => {
			if (state !== nextState) {
				_setState(nextState)
			}

			if (stateControlled !== nextState) {
				setStateControlled?.(nextState)
			}
		},
		[state, stateControlled, _setState, setStateControlled]
	)

	return [state, setState]
}

export default useControlledState
