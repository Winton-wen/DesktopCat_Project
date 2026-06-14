# Action-Bound Bubble Lifecycle Design

## Goal

Keep action-triggered speech visible only while its matching action is active.
When that action finishes or is replaced, its current or queued bubble must be
removed so later animation never appears with stale copy.

## Design

- Each started action receives a monotonically increasing action token.
- Speech created for that action is shown with the current token as its owner.
- `RigSpeechBubble` records the owner of the visible bubble and of queued
  bubbles.
- When an action finishes or is replaced, the app asks the bubble to clear that
  token. A matching visible bubble is hidden, and matching queued bubbles are
  discarded.
- Bubbles without an owner remain independent. Fixed reminders, return-home
  completion copy, and other state-only messages keep their existing timers and
  queue behavior.

## Behavior

- Natural action completion closes its matching bubble immediately.
- Drag, wake, first launch, visual-tour force paths, and other forced action
  replacements close the replaced action's bubble.
- Finishing an action does not close a fixed reminder or unrelated state
  bubble.
- A queued action bubble that never became visible is discarded when its action
  ends.

## Tests

- An action-owned visible bubble is cleared when the action finishes.
- An action-owned queued bubble is discarded when the action finishes.
- An unowned reminder bubble is preserved when an action finishes.
- Replacing an action clears the previous action token before starting the new
  action.

