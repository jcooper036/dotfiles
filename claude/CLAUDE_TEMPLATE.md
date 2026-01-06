# Purpose and Scope
What is this area responsible for? What it explicitly doesn't do.

# Entry Points & Contracts
Main APIs, jobs, CLI commands. Invariants like "All outbound calls go through this client" or "This is the only enforcement point for age-based ad policy"

# Usage Patterns
Canonical examples "To add a new rule, follow this pattern..."

# Anti-patterns
Negative examples: "Never call this directly from controllers; go through X"

# Dependencices & Edges
Which other directories or services it depends on

# Patterns and Pitfalls
Things that reatedly confused agents or humans: "This looks stateless but uses shared mutable state" "This config is overridden at deploy time; don't trust the default"

