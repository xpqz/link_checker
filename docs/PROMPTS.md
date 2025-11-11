# Prompts

## Make a plan

Here is our job for today: creating a document `docs/PLAN.md`. No implementation yet, just a plan. My goal is to (a) write a docker compose setup that renders the mkdocs site and serves it. I want to serve it in Docker, using nginx for speed. (b), create a tool link_check/link_check.py which should spider the site as served in Docker, and verify every link, reporting back on any 404s. The report should be in yaml, and map the page to any broken links. Also verify the nav itself: if any links presented by the nav are broken, report those, too. First, carefully construct a detailed plan for (a) and (b), considering how we can iterate and especially test each step. Consider performance for (b). Note CAREFULLY, considering the implications: as we're always running against a local Docker container, we're compute bound, NOT IO bound: we want multiple processes, not any async-io mess. Fast, concise, simple to understand and correct.

## Make a TODO

Write a detailed document `docs/TODO.md`, derived from `docs/PLAN.md` which breaks the plan into task-sized chunks of a suitable granularity that can be tested in isolation.


## Set up git

Initalise a NEW git repository

Let's make an upstream GitHub repository for this, called `doc-link-check`, using `gh`

Create a label 'epic' on github

## Make Epics and Issues

From `docs/TODO.md`, create two Epic issues: one for the serving, and one for the link checking. They should each clearly state the scope (from the TODO and or PLAN), and list a set of sub-tasks, with check boxes, linking to issues you create for each task. Label the epics with the 'epic' label.

## Set up dev environment

Initialise a python project using "uv". We want tests using "pytest", formatting with "black", and linting with "ruff". Create a git commit hook that runs all tests, formats with black and lints with ruff. Demonstrate that this is functional.