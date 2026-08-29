#!/usr/bin/env bash

set -Eeuo pipefail
IFS=$'\n\t'
umask 077
export LC_ALL=C
export GIT_NO_REPLACE_OBJECTS=1
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_TERMINAL_PROMPT=0
export GIT_PAGER=cat
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE \
    GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES \
    GIT_REPLACE_REF_BASE GIT_NAMESPACE GIT_EXEC_PATH \
    GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_CONFIG_SYSTEM \
    GIT_EXTERNAL_DIFF GIT_DIFF_OPTS GIT_PAGER_IN_USE GIT_ASKPASS SSH_ASKPASS

set_safe_directories() {
    local index=0 safe_path
    for safe_path in "$@"; do
        export "GIT_CONFIG_KEY_${index}=safe.directory"
        export "GIT_CONFIG_VALUE_${index}=$safe_path"
        index=$((index + 1))
    done
    export GIT_CONFIG_COUNT="$index"
}

usage() {
    cat <<'EOF'
Usage: create-worktree.sh --repo-root PATH --work-root PATH --job-id ID
                          --base-ref COMMIT [--branch task/ID-slug]

Create one isolated Git worktree below WORK_ROOT/worktrees. Without --branch,
the worktree is detached. Inputs are deliberately narrow; refs must be immutable
commit object IDs and task branches must follow the VISION-64 convention.
EOF
}

die() {
    printf 'create-worktree: %s\n' "$*" >&2
    exit 1
}

canonical_dir() {
    [[ -d "$1" ]] || die "directory does not exist: $1"
    (cd -- "$1" && pwd -P)
}

repo_root=''
work_root=''
job_id=''
base_ref=''
branch=''

while (($#)); do
    case "$1" in
        --repo-root)
            (($# >= 2)) || die 'missing value for --repo-root'
            repo_root=$2
            shift 2
            ;;
        --work-root)
            (($# >= 2)) || die 'missing value for --work-root'
            work_root=$2
            shift 2
            ;;
        --job-id)
            (($# >= 2)) || die 'missing value for --job-id'
            job_id=$2
            shift 2
            ;;
        --base-ref)
            (($# >= 2)) || die 'missing value for --base-ref'
            base_ref=$2
            shift 2
            ;;
        --branch)
            (($# >= 2)) || die 'missing value for --branch'
            branch=$2
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "unknown argument: $1"
            ;;
    esac
done

[[ -n "$repo_root" ]] || die '--repo-root is required'
[[ -n "$work_root" ]] || die '--work-root is required'
[[ -n "$job_id" ]] || die '--job-id is required'
[[ -n "$base_ref" ]] || die '--base-ref is required'
[[ "$work_root" == /* ]] || die '--work-root must be an absolute path'
[[ "$job_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]] ||
    die '--job-id must contain 1-64 safe identifier characters'
[[ "$base_ref" =~ ^[0-9a-fA-F]{40}([0-9a-fA-F]{24})?$ ]] ||
    die '--base-ref must be a full 40- or 64-character commit object ID'

repo_root=$(canonical_dir "$repo_root")
set_safe_directories "$repo_root"
git_top=$(git -C "$repo_root" rev-parse --show-toplevel 2>/dev/null) ||
    die '--repo-root is not a Git worktree'
git_top=$(canonical_dir "$git_top")
[[ "$git_top" == "$repo_root" ]] || die '--repo-root must name the repository root'

command -v realpath >/dev/null 2>&1 || die 'realpath executable not found'
[[ "$work_root" != / ]] || die 'refusing to use / as the work root'
work_root=$(realpath -m -- "$work_root")
[[ "$work_root" != "$repo_root" ]] || die 'work root must be outside the repository'
[[ "$work_root" != "$repo_root"/* ]] || die 'work root must be outside the repository'
[[ "$repo_root" != "$work_root"/* ]] || die 'repository must be outside the work root'
mkdir -p -- "$work_root"
work_root=$(canonical_dir "$work_root")

base_commit=$(git -C "$repo_root" rev-parse --verify "$base_ref^{commit}" 2>/dev/null) ||
    die 'base commit is not available in the repository'
[[ "$base_commit" == "${base_ref,,}" ]] || die '--base-ref must resolve exactly to the supplied commit ID'

if [[ -n "$branch" ]]; then
    [[ "$branch" =~ ^task/[1-9][0-9]*-[a-z0-9]+(-[a-z0-9]+)*$ ]] ||
        die '--branch must match task/<numeric-id>-<lowercase-kebab-slug>'
    git check-ref-format --branch "$branch" >/dev/null 2>&1 || die 'invalid Git branch name'
    if git -C "$repo_root" show-ref --verify --quiet "refs/heads/$branch"; then
        die "local branch already exists: $branch"
    fi
fi

worktrees_root="$work_root/worktrees"
mkdir -p -- "$worktrees_root"
worktrees_root=$(canonical_dir "$worktrees_root")
worktree_path="$worktrees_root/$job_id"
[[ "$worktree_path" == "$worktrees_root"/* ]] || die 'derived worktree escaped the work root'
[[ ! -e "$worktree_path" && ! -L "$worktree_path" ]] || die "worktree path already exists: $worktree_path"

if [[ -n "$branch" ]]; then
    git -C "$repo_root" -c core.hooksPath=/dev/null -c core.fsmonitor=false \
        worktree add -b "$branch" "$worktree_path" "$base_commit" >&2
else
    git -C "$repo_root" -c core.hooksPath=/dev/null -c core.fsmonitor=false \
        worktree add --detach "$worktree_path" "$base_commit" >&2
fi

set_safe_directories "$repo_root" "$worktree_path"
created_top=$(git -C "$worktree_path" rev-parse --show-toplevel 2>/dev/null) ||
    die 'created path is not a Git worktree'
created_top=$(canonical_dir "$created_top")
[[ "$created_top" == "$worktree_path" ]] || die 'created worktree resolved outside its assigned path'
created_commit=$(git -C "$worktree_path" rev-parse HEAD)
[[ "$created_commit" == "$base_commit" ]] || die 'created worktree is not at the requested base commit'

printf '%s\n' "$worktree_path"
