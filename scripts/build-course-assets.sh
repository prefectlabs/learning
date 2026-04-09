#!/bin/bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: build-course-assets.sh [--apply|--check] [PATH...]

If no PATH arguments are provided, the script inspects staged files in apply
mode and the current working tree in check mode.
EOF
}

mode="check"
declare -a inputs=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply)
      mode="apply"
      ;;
    --check)
      mode="check"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      inputs+=("$@")
      break
      ;;
    *)
      inputs+=("$1")
      ;;
  esac
  shift
done

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [ "${#inputs[@]}" -eq 0 ]; then
  if [ "$mode" = "apply" ]; then
    while IFS= read -r -d '' path; do
      inputs+=("$path")
    done < <(git diff --cached --name-only -z --diff-filter=ACMR)
  else
    while IFS= read -r -d '' path; do
      inputs+=("$path")
    done < <(git diff --name-only -z --diff-filter=ACMR)
  fi
fi

append_unique_root() {
  local root="$1"

  if [ -n "$seen_roots" ] && printf '%s\n' "$seen_roots" | grep -Fxq "$root"; then
    return 0
  fi

  seen_roots="${seen_roots}${seen_roots:+
}$root"
  course_roots+=("$root")
}

find_course_root() {
  local candidate="$1"
  local dir

  if [ -d "$candidate" ]; then
    dir="$candidate"
  else
    dir="$(dirname "$candidate")"
  fi

  while [ "$dir" != "." ] && [ "$dir" != "/" ]; do
    if [ -f "$dir/track.yml" ]; then
      printf '%s\n' "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done

  return 1
}

declare -a course_roots=()
seen_roots=""

for path in "${inputs[@]}"; do
  [ -n "$path" ] || continue

  if ! root="$(find_course_root "$path")"; then
    continue
  fi

  case "$root" in
    courses/*) ;;
    *) continue ;;
  esac

  append_unique_root "$root"
done

for root in "${course_roots[@]}"; do
  build_script="$root/build-assets"

  if [ ! -f "$build_script" ]; then
    continue
  fi

  echo "Building assets for $root"
  (
    cd "$root"
    bash ./build-assets
  )

  if [ "$mode" = "apply" ]; then
    if [ -d "$root/assets" ]; then
      git add -A "$root/assets"
    fi
    continue
  fi

  if [ -n "$(git status --porcelain --untracked-files=all -- "$root/assets")" ]; then
    echo "Asset build changed tracked output in $root."
    echo "Re-run build-assets and commit the updated assets."
    git status --short -- "$root/assets"
    exit 1
  fi
done
