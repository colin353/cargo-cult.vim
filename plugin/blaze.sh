#!/bin/bash

FILE=$(bazel query $2)
PACKAGE=$(bazel query $2 --output=package)
TARGET=$(bazel query "attr('srcs', $FILE, ${FILE//:*/}:*)" | head -n 1)
TEST_TARGET=$(bazel query "kind('.*test rule', attr('srcs', $FILE, ${FILE//:*/}:*))" 2>/dev/null | head -n 1)

if [ "$1" == "test" ]; then
  # Need to identify the tests which depend on this file, and run those. Pick the first one.
  if [ -z "$TEST_TARGET" ]; then
     TEST_TARGET=$(bazel query "kind('.*test rule', rdeps(//$PACKAGE/..., $TARGET))" | head -n 1)
  fi
  bazel test $TEST_TARGET --noshow_progress --test_output=errors 2>&1 | grep -v -e "^INFO:" -e "^FAILED:" -e "^ERROR:"
elif [ "$1" == "build" ]; then
  bazel build $TARGET --noshow_progress 2>&1 | grep -v -e "^INFO:" -e "^FAILED:" -e "^ERROR:"
else
  # Otherwise just build the corresponding target
  bazel $1 $TARGET
fi

