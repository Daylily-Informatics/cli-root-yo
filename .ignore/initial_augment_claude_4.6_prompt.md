# What I typed in

ignore everything in  .ignore/*, then please familiarize yourself rules in  ~/.augmnet/* and .augment/*, then review the requirements in SPEC.md and please write a SPEC_IMPLEMENTATION_PLAN.md, return to me when done so i may review and approve

# following the prompt improving button

Please perform the following tasks in sequence:

1. **Ignore all files in `.ignore/` directory** - Do not reference or use any content from `.ignore/*` for implementation guidance.

2. **Review all rule files** - Familiarize yourself with:
   - Global rules in `~/.augment/rules/*.md` (note: corrected typo from "augmnet")
   - Project-specific rules in `.augment/*.md` (if any exist)

3. **Study the specification** - Thoroughly review `SPEC.md` which contains the complete normative specification for `cli-root-yo`.

4. **Create an implementation plan** - Write a new file `SPEC_IMPLEMENTATION_PLAN.md` that includes:
   - A breakdown of implementation phases/milestones
   - Module-by-module implementation order (following the structure in SPEC.md Section 3.2)
   - Dependencies between modules
   - Testing strategy for each phase
   - Migration validation checkpoints
   - Estimated complexity/risk for each component
   - Any clarifying questions or ambiguities that need resolution before implementation begins

5. **Present for review** - After creating `SPEC_IMPLEMENTATION_PLAN.md`, notify me that it's ready for review and approval before proceeding with actual implementation.

**Critical constraints:**
- Follow the SPEC.md requirements exactly as written (Section 8: "DO NOT CHANGE" rules)
- Do not begin implementation until the plan is approved
- The plan should be detailed enough that implementation can proceed deterministically once approved