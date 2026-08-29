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

usage() {
    cat <<'EOF'
Usage: verify-candidate.sh --repo-root PATH --work-root PATH --job-id ID
                           --base-ref COMMIT --profile smoke|candidate
                           [--branch task/ID-slug]
                           [--task-spec docs/tasks/ID-slug.md]
                           [--allow-path PATH ...]

Perform structural, non-executing verification. This script never evaluates a
task body and never runs code from the candidate checkout.
EOF
}

die() {
    printf 'verify-candidate: %s\n' "$*" >&2
    exit 1
}

canonical_dir() {
    [[ -d "$1" ]] || die "directory does not exist: $1"
    (cd -- "$1" && pwd -P)
}

valid_relative_path() {
    local value=$1
    [[ -n "$value" && "$value" != /* && "$value" != *'//'* ]] || return 1
    [[ "$value" =~ ^[A-Za-z0-9._/-]+$ ]] || return 1
    [[ "/$value/" != *'/../'* && "/$value/" != *'/./'* ]] || return 1
    [[ "$value" != .git && "$value" != .git/* ]] || return 1
}

path_allowed() {
    local changed=$1
    local allowed
    for allowed in "${allow_paths[@]}"; do
        if [[ "$allowed" == */ ]]; then
            [[ "$changed" == "$allowed"* ]] && return 0
        elif [[ "$changed" == "$allowed" ]]; then
            return 0
        fi
    done
    return 1
}

repo_root=''
work_root=''
job_id=''
base_ref=''
profile=''
branch=''
task_spec=''
declare -a allow_paths=()
max_changed_files=64
max_file_bytes=1048576
max_total_bytes=4194304

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
        --profile)
            (($# >= 2)) || die 'missing value for --profile'
            profile=$2
            shift 2
            ;;
        --branch)
            (($# >= 2)) || die 'missing value for --branch'
            branch=$2
            shift 2
            ;;
        --task-spec)
            (($# >= 2)) || die 'missing value for --task-spec'
            task_spec=$2
            shift 2
            ;;
        --allow-path)
            (($# >= 2)) || die 'missing value for --allow-path'
            allow_paths+=("$2")
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

[[ -n "$repo_root" && -n "$work_root" && -n "$job_id" && -n "$base_ref" && -n "$profile" ]] ||
    die '--repo-root, --work-root, --job-id, --base-ref, and --profile are required'
[[ "$profile" == smoke || "$profile" == candidate ]] || die '--profile must be smoke or candidate'
[[ "$job_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]] || die 'invalid job ID'
[[ "$base_ref" =~ ^[0-9a-fA-F]{40}([0-9a-fA-F]{24})?$ ]] || die 'base ref must be a full commit ID'
[[ "$work_root" == /* ]] || die '--work-root must be absolute'

if [[ "$profile" == smoke ]]; then
    [[ -z "$branch" ]] || die 'smoke verification requires a detached worktree'
    [[ -z "$task_spec" ]] || die 'smoke verification rejects a task spec'
    ((${#allow_paths[@]} == 0)) || die 'smoke verification does not accept path allowances'
else
    [[ "$branch" =~ ^task/[1-9][0-9]*-[a-z0-9]+(-[a-z0-9]+)*$ ]] || die 'candidate branch is invalid'
    [[ "$task_spec" =~ ^docs/tasks/[1-9][0-9]*-[a-z0-9]+(-[a-z0-9]+)*\.md$ ]] ||
        die 'candidate task spec is invalid'
    task_name=${task_spec#docs/tasks/}
    task_name=${task_name%.md}
    [[ "$branch" == "task/$task_name" ]] || die 'candidate branch and task spec do not match'
    ((${#allow_paths[@]} > 0)) || die 'candidate verification requires at least one --allow-path'
fi

for allowed in "${allow_paths[@]}"; do
    valid_relative_path "$allowed" || die "invalid allowed path: $allowed"
done

repo_root=$(canonical_dir "$repo_root")
work_root=$(canonical_dir "$work_root")
command -v realpath >/dev/null 2>&1 || die 'realpath executable not found'
command -v stat >/dev/null 2>&1 || die 'stat executable not found'
[[ "$work_root" != / && "$work_root" != "$repo_root" && "$work_root" != "$repo_root"/* ]] ||
    die 'invalid work-root boundary'
worktree_path="$work_root/worktrees/$job_id"
evidence_dir="$work_root/evidence/$job_id"
worktree_path=$(canonical_dir "$worktree_path")
evidence_dir=$(canonical_dir "$evidence_dir")
[[ "$worktree_path" == "$work_root/worktrees/"* ]] || die 'worktree escaped its boundary'
[[ "$evidence_dir" == "$work_root/evidence/"* ]] || die 'evidence directory escaped its boundary'

registered=false
while IFS= read -r registered_path; do
    if [[ -d "$registered_path" ]]; then
        registered_path=$(canonical_dir "$registered_path")
    fi
    if [[ "$registered_path" == "$worktree_path" ]]; then
        registered=true
        break
    fi
done < <(git -C "$repo_root" worktree list --porcelain | sed -n 's/^worktree //p')
[[ "$registered" == true ]] || die 'candidate path is not a registered worktree of the repository'

base_commit=$(git -C "$repo_root" rev-parse --verify "$base_ref^{commit}" 2>/dev/null) || die 'base commit unavailable'
[[ "$base_commit" == "${base_ref,,}" ]] || die 'base ref did not resolve exactly'
head_commit=$(git -C "$worktree_path" rev-parse HEAD)

if [[ "$profile" == candidate ]]; then
    task_spec_path="$worktree_path/$task_spec"
    [[ -f "$task_spec_path" && ! -L "$task_spec_path" ]] ||
        die 'candidate task spec is missing, not regular, or a symlink'
    git -C "$worktree_path" cat-file -e "$base_commit:$task_spec" 2>/dev/null ||
        die 'candidate task spec is not committed at the base revision'
    base_task_blob=$(git -C "$worktree_path" rev-parse "$base_commit:$task_spec")
    current_task_blob=$(git -C "$worktree_path" hash-object "$task_spec_path")
    [[ "$base_task_blob" == "$current_task_blob" ]] || die 'candidate changed its governing task spec'
fi

git -C "$worktree_path" status --porcelain=v1 --untracked-files=all >"$evidence_dir/git-status.txt"
changed_paths_file="$evidence_dir/changed-paths.txt"
: >"$changed_paths_file"
declare -a changed_paths=()
declare -a untracked_paths=()
while IFS= read -r -d '' changed; do
    valid_relative_path "$changed" || die "candidate produced an unsupported path: $changed"
    changed_paths+=("$changed")
done < <(git -C "$worktree_path" diff --name-only -z "$base_commit" --)
while IFS= read -r -d '' changed; do
    valid_relative_path "$changed" || die "candidate produced an unsupported path: $changed"
    changed_paths+=("$changed")
    untracked_paths+=("$changed")
done < <(git -C "$worktree_path" ls-files --others --exclude-standard -z)
if ((${#changed_paths[@]} > 0)); then
    printf '%s\n' "${changed_paths[@]}" >>"$changed_paths_file"
fi
sort -u -o "$changed_paths_file" "$changed_paths_file"

declare -a unique_paths=()
while IFS= read -r changed; do
    [[ -n "$changed" ]] && unique_paths+=("$changed")
done <"$changed_paths_file"
changed_paths=("${unique_paths[@]}")
(( ${#changed_paths[@]} <= max_changed_files )) ||
    die "candidate changed more than $max_changed_files files"

total_bytes=0
for changed in "${changed_paths[@]}"; do
    candidate_path="$worktree_path/$changed"
    path_cursor="$worktree_path"
    IFS='/' read -r -a path_components <<<"$changed"
    for component in "${path_components[@]}"; do
        [[ -n "$component" ]] || continue
        path_cursor="$path_cursor/$component"
        [[ ! -L "$path_cursor" ]] || die "candidate path traverses a symlink: $changed"
    done
    if [[ -e "$candidate_path" || -L "$candidate_path" ]]; then
        [[ -f "$candidate_path" && ! -L "$candidate_path" ]] ||
            die "candidate path is not a regular file: $changed"
        resolved_path=$(realpath -e -- "$candidate_path") || die "unable to resolve candidate path: $changed"
        [[ "$resolved_path" == "$worktree_path"/* ]] || die "candidate path escaped its worktree: $changed"
        file_bytes=$(stat -c '%s' -- "$candidate_path") || die "unable to size candidate path: $changed"
        ((file_bytes <= max_file_bytes)) || die "candidate file exceeds $max_file_bytes bytes: $changed"
        total_bytes=$((total_bytes + file_bytes))
        ((total_bytes <= max_total_bytes)) || die "candidate files exceed $max_total_bytes total bytes"
    fi
done

git -C "$worktree_path" diff --binary --no-ext-diff "$base_commit" -- >"$evidence_dir/candidate.patch"
git -C "$worktree_path" diff --check "$base_commit" -- >"$evidence_dir/diff-check.txt"
for changed in "${untracked_paths[@]}"; do
    set +e
    git -C "$worktree_path" diff --no-index --binary -- /dev/null "$changed" \
        >>"$evidence_dir/candidate.patch" 2>>"$evidence_dir/untracked-diff-errors.txt"
    untracked_diff_status=$?
    git -C "$worktree_path" diff --no-index --check -- /dev/null "$changed" \
        >>"$evidence_dir/diff-check.txt" 2>>"$evidence_dir/untracked-diff-errors.txt"
    untracked_check_status=$?
    set -e
    ((untracked_diff_status == 0 || untracked_diff_status == 1)) ||
        die "failed to capture untracked candidate path: $changed"
    ((untracked_check_status == 0 || untracked_check_status == 1)) ||
        die "failed to check untracked candidate path: $changed"
done
[[ ! -s "$evidence_dir/diff-check.txt" ]] || die 'candidate contains whitespace errors'

if [[ "$profile" == smoke ]]; then
    [[ "$head_commit" == "$base_commit" ]] || die 'smoke worktree HEAD moved from the base commit'
    [[ ! -s "$evidence_dir/git-status.txt" ]] || die 'smoke worktree is not clean'
    [[ ! -s "$changed_paths_file" ]] || die 'smoke worktree contains changes'
    detached=$(git -C "$worktree_path" symbolic-ref -q --short HEAD || true)
    [[ -z "$detached" ]] || die 'smoke worktree is not detached'
    head_state=detached
else
    actual_branch=$(git -C "$worktree_path" symbolic-ref -q --short HEAD || true)
    [[ "$actual_branch" == "$branch" ]] || die 'candidate is not on its assigned branch'
    [[ "$head_commit" == "$base_commit" ]] || die 'agent candidate must not create commits'
    head_state=$actual_branch
    git -C "$worktree_path" merge-base --is-ancestor "$base_commit" HEAD || die 'candidate history does not descend from its base'
    for changed in "${changed_paths[@]}"; do
        [[ "$changed" != "$task_spec" ]] || die 'candidate changed its governing task spec'
        path_allowed "$changed" || die "changed path is outside the task allowlist: $changed"
    done
fi

{
    printf 'check=structural-only\n'
    printf 'note=not-forge-verify-or-proof\n'
    printf 'profile=%s\n' "$profile"
    printf 'base_commit=%s\n' "$base_commit"
    printf 'head_commit=%s\n' "$head_commit"
    printf 'head_state=%s\n' "$head_state"
    [[ "$profile" == smoke ]] || printf 'task_spec=%s\n' "$task_spec"
    printf 'result=pass\n'
} >"$evidence_dir/verification.env"

printf 'verification passed (%s)\n' "$profile"
