# Current Motion Failures

These actions are not acceptable for the QQ-pet-quality route:

- `sleep_in`: collapses by flattening the cat instead of using a natural sleepy
  settle-down.
- `wake`: returns to sitting too abruptly and reads as a pose jump.
- `happy`: previous synthetic replacement was rejected because it was built
  from transformed idle frames. `happy_cute_keyposes_v1` now provides real
  redrawn key poses, but still needs generated or hand-cleaned in-betweens
  before it can be considered final production quality.
- `cute`: previous synthetic replacement was rejected because it was built
  from transformed idle frames. `happy_cute_keyposes_v1` now provides real
  redrawn paw-tuck/head-tilt key poses, but still needs generated or
  hand-cleaned in-betweens before promotion.
- `walk` / `walk_left`: source frames need better foot alternation and body
  mechanics. Runtime now adds desktop displacement, but the art still needs a
  polished walk cycle.

Do not promote a new candidate as visually improved until these actions are
replaced or hand-cleaned and pass visual review.
