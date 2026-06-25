```
name: pr-review
description: Instructions on PR review
```

# We are writing a review
You'll be given a PR on github

## Tooling
-use `gh` tools where applicable

## Use multiple agents to review
Tell each agent that they are to write a review of the PR, posting their review as 
"""
# <AGENT NAME> REVIEW
<review content>
"""
- all agents are allowed to write comments on specific lines using gh tooling
- tell the agents to post their review and then exit
- send the following specifications to the agents when they are started
- never comment on the level or quality of work
- terse, direct, response

### Code agent
- Every line of code is tech debt
- You are looking for senior / staff level code
- ALWAYS avoid numbering sections of the code in comments
    - ex: "Step 0: ...."
    - this is an anti-pattern. what if we add a step or remove one later?
- Code == truth, comments == a lie about what the code did at some point
    - comments are RARELY necessary, and should almost always be removed
- Look for places where multiple pieces of code follow the same pattern - potential abstraction
- Always step back and ask "what are we trying to do here? Did whoever was writing this get lost in complexity vs accomplishing the objective?"
- Think through input edge cases, and how that can have un-intended consequences
- faked, stubbed, dummy capabiltiies, etc, are only OK if the product specs (from BEFORE the PR) explicitly allow for it. Otherwise, this is usually the sign of someone not doing their job.

#### python
- naked try / except is NEVER allowed
    - try / except should be used very sparsly
    - it must always have SPECIFIC error handling
    - most times the real question is "why can this fail? should it be written in a way that it can't?"
    - the main exception is when dealing with external API calls (i.e. not our code)
- never import from _future - this is an anti-pattern in old code
- never import typing to use types (use built-in types like list, dict, etc)
    - exception is when dealing with generics (i.e. you actually need functionality from the typing module)
- for computation, prefer numpy array / matrix methods
- prefer Pydantic for data classes

#### tests
TESTS ARE TECH DEBT. In the literal sense, we are writing more code than we need to in order to accelerate future development (by preventing bugs, regressions, etc). They should be treated as having a cost.

ONE OF THE WORST BUGS is a misbehaviing test. Future devs will naively expect tests to pass, so tests that test extranious function or content are the worst kind of limiting.

A valid critique of a PR is that there are too many tests.

Tests should be limited, and test a small number of things
- Tests should test edge cases (i.e. input boundaries)
- They can test integration of multiple functions
- EXTERNAL interfaces (i.e. the expected interface of a service). When this is the case, the test MUST come with a comment link to documentation about the interface
- regression tests can test that we get the correct value from functions that change values

Tests should NEVER
- test basic programming concepts (a function is a loop, and the test is testing that it loops)
- INTERNAL interfaces. Define these with pydantic models, classes, Protocols, etc. NEVER with tests
- that an interface class (i.e. pydantic) "works" (i.e. I made an object of type X, oh look it has properties of type X, useless lazy test)


### Documentation Agent
Along with clarity of writing, make sure to look for the following
- duplication of documentation. a little is ok
- brevity (most things in the docs are too long winded)
- logical contridictions
- over-specification (the documents should be about requirments, decisions, philosophy, architecture, etc. When details get too much like code, they have the potential to conflict with future code, and thus are dead weight
- ALWAYS ask : is this core to the product? If someone decides to do this differently, will the product change?
- Make sure that READMEs, AGENTS.md, CLAUDE.md files are maintained and sparse. the goal is to enable performance and avoid future confusion
- Condense old plans into modern updates, remove stale information

