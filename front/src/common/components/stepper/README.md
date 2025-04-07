
## Description


The Stepper is a component that allows managing step-by-step navigation in the interface. It consists of two main parts:


1. A Provider (`StepperProvider`) that manages state and logic
2. A component (`Stepper`) that displays the stepper and handles navigation between steps


## Usage

### 1. Step Definition


Each step must follow this interface :

```typescript
type Step<Key extends string> = {
  key: Key
  title: ReactNode
  allowNextStep?: boolean // Optional: allows controlling whether the next step is accessible
}
```


### 2. Provider Configuration


Wrap your component with the `StepperProvider` and pass it the steps:

```typescript
const steps = [
  { key: "step1", title: "Étape 1" },
  { key: "step2", title: "Étape 2", allowNextStep: false },
  { key: "step3", title: "Étape 3" }
]

return (
  <StepperProvider steps={steps}>
    <YourComponent />
  </StepperProvider>
)
```


### 3. Using in Child Components


In your components, use the `useStepper` hook to access the functionality:

```typescript
const {
  currentStep,          // Étape courante
  currentStepIndex,     // Index de l'étape courante (commence à 1)
  previousStep,         // Étape précédente
  nextStep,            // Étape suivante
  goToNextStep,        // Fonction pour aller à l'étape suivante
  goToPreviousStep,    // Fonction pour aller à l'étape précédente
  setStep              // Fonction pour aller à une étape spécifique
} = useStepper()
```


### 4. Displaying the Stepper

The `Stepper` component can be used in two ways:

- By using the DSFR component directly without using a Provider system

```typescript
  <BaseStepper
    title="current title"
    stepCount={4}
    currentStep={0}
    nextTitle="next title"
  />
```

- By using the `Stepper` component with the provider and the associated components

```typescript
const MyComponent = () => {
  const steps = [
    { key: "step1", title: "Étape 1" },
    { key: "step2", title: "Étape 2" },
    { key: "step3", title: "Étape 3" }
  ]

  return (
    <StepperProvider steps={steps}>
      <div>
        <Stepper />
        <StepContent />
        <div>
          <Stepper.Previous />
          <Stepper.Next />
        </div>
      </div>
    </StepperProvider>
  )
}
```


## Important notes


- The `currentStepIndex` starts at 1 for display
- The `allowNextStep` property allows dynamically controlling whether the user can move to the next step