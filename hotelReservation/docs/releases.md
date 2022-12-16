## Releasing

Docker images in the project are very important for both development and
deployment. As a consequence, it is important that they remain up to date with
the latest code changes. To achieve this, we rely on Github tags.

Any time you introduce a relevant change to the codebase, consider creating
a new tag. Tags are first created from your branch. So before creating a branch,
make sure you have an open PR with your changes.

Then, from _outside_ the container, bump the code version in all the files that
keep track of it:

```bash
source ./bin/workon.sh

# Bump the code version
inv git.bump
```

Check the files that have been changed (and ensure only code versions have
changed), commit and push the changes. Then, tag the code:

```bash
inv git.tag
```

This will push a new tag to Github, which will also trigger a re-build of the
docker image. After that is finished, you can now run the tests on the PR,
which will use the just built image.

Once the tests pass, and the PR is merged in, you will have to re-tag the code
to ensure a clean Git log:

```bash
# Get your just merged commit
git checkout main
git pull origin main

# Ensure it is the latest version
cat VERSION

# Re-tag
inv git.tag --force
```

### Publishing a release

Releases are published according to no special criteria, every now and then,
pinned to a tag. So, if after bumping the code version you feel that the
changes since the last release are relevant enough, create a release.

Note that it is important that you create and publish a release from the `main`
branch, **not** from your current PR branch.

First, you will create a draft release. From outside the container do:

```bash
inv git.create-release
```

Then you can navigate to the [Releases](https://github.com/intel-sandbox/carlosse.DeathStarBench/releases)
tab in the repository, and check that the draft release looks alright. If
something does not look right, just delete the release, and create it again.

Once the draft release looks good, you may publish it:

```bash
inv git.publish-release
```

### Note on the `base` image

The `base` image is not meant to change often. If you add another dependency to
the project and you need to change the `base` image, make sure you re-tag it
yourself. See the [docker](./docker.md) docs for more details.

In short, once you are happy with the process run from outside the container:

```bash
inv docker.build --target base --push
```

Note that the previous command can take around 30 minutes depending on your
machine.
