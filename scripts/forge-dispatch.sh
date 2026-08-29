#!/usr/bin/env bash

set -Eeuo pipefail
IFS=$'\n\t'
umask 077
export LC_ALL=C
# Do not let caller-controlled Git configuration, replacement refs, alternates,
# hooks, or external diff helpers influence coordinator decisions.
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
Usage: forge-dispatch.sh --repo-root PATH --work-root PATH --job-id ID
                         --base-ref COMMIT [--mode smoke|dry-run|execute]
                         [--agent none|codex|claude]
                         [--task-id N --slug SLUG --task-spec PATH]
                         [--allow-path PATH ...] [--timeout-seconds N]

The default is an agentless, mutation-free smoke run. Dry-run validates a
reviewed task and selected wrapper but invokes no model. Execute is rejected
during Gate F; enabling it requires a separately reviewed security design.
Issue bodies are never accepted as commands or arguments by this interface.
EOF
}

die() {
    printf 'forge-dispatch: %s\n' "$*" >&2
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

bootstrap_path_allowed() {
    case "$1" in
        docs/*|AGENTS.md|CLAUDE.md|README.md)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

task_spec_is_approved_at() {
    local repository=$1
    local commit=$2
    local spec=$3
    local object_type task_bytes schema_count status_count approved_count

    object_type=$(git -C "$repository" cat-file -t "$commit:$spec" 2>/dev/null) || return 1
    [[ "$object_type" == blob ]] || return 1
    task_bytes=$(git -C "$repository" cat-file -s "$commit:$spec" 2>/dev/null) || return 1
    ((task_bytes > 0 && task_bytes <= 65536)) || return 1
    schema_count=$(git -C "$repository" cat-file blob "$commit:$spec" |
        grep -Ec '^- Schema: `vision-task-v1`([[:space:]]|$)' || true)
    status_count=$(git -C "$repository" cat-file blob "$commit:$spec" |
        grep -Ec '^- Status:' || true)
    approved_count=$(git -C "$repository" cat-file blob "$commit:$spec" |
        grep -Ec '^- Status: `approved`([[:space:]]|$)' || true)
    [[ "$schema_count" == 1 && "$status_count" == 1 && "$approved_count" == 1 ]]
}

repo_root=''
work_root=''
job_id=''
base_ref=''
mode='smoke'
agent='none'
task_id=''
slug=''
task_spec=''
timeout_seconds=1800
declare -a allow_paths=()

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
        --mode)
            (($# >= 2)) || die 'missing value for --mode'
            mode=$2
            shift 2
            ;;
        --agent)
            (($# >= 2)) || die 'missing value for --agent'
            agent=$2
            shift 2
            ;;
        --task-id)
            (($# >= 2)) || die 'missing value for --task-id'
            task_id=$2
            shift 2
            ;;
        --slug)
            (($# >= 2)) || die 'missing value for --slug'
            slug=$2
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
        --timeout-seconds)
            (($# >= 2)) || die 'missing value for --timeout-seconds'
            timeout_seconds=$2
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

[[ -n "$repo_root" && -n "$work_root" && -n "$job_id" && -n "$base_ref" ]] ||
    die '--repo-root, --work-root, --job-id, and --base-ref are required'
[[ "$work_root" == /* ]] || die '--work-root must be absolute'
[[ "$job_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]] || die 'invalid job ID'
[[ "$base_ref" =~ ^[0-9a-fA-F]{40}([0-9a-fA-F]{24})?$ ]] || die 'base ref must be a full commit ID'
[[ "$mode" == smoke || "$mode" == dry-run || "$mode" == execute ]] || die 'invalid mode'
[[ "$agent" == none || "$agent" == codex || "$agent" == claude ]] || die 'invalid agent'
[[ "$timeout_seconds" =~ ^[1-9][0-9]*$ ]] || die 'timeout must be a positive decimal integer without leading zeroes'
((timeout_seconds >= 60 && timeout_seconds <= 3600)) || die 'timeout must be between 60 and 3600 seconds'

[[ "$mode" != execute ]] || die 'execute mode is disabled during Gate F; use smoke or dry-run'

if [[ "$mode" == smoke ]]; then
    [[ "$agent" == none ]] || die 'smoke mode requires --agent none'
    [[ -z "$task_id" && -z "$slug" && -z "$task_spec" ]] || die 'smoke mode rejects task inputs'
    ((${#allow_paths[@]} == 0)) || die 'smoke mode rejects path allowances'
else
    [[ "$agent" == codex || "$agent" == claude ]] || die "$mode mode requires codex or claude"
    [[ "$task_id" =~ ^[1-9][0-9]*$ ]] || die 'task ID must be a positive decimal integer without leading zeroes'
    [[ "$slug" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || die 'slug must be lowercase kebab-case'
    expected_task_spec="docs/tasks/$task_id-$slug.md"
    [[ "$task_spec" == "$expected_task_spec" ]] || die "task spec must be $expected_task_spec"
    ((${#allow_paths[@]} > 0)) || die "$mode mode requires at least one --allow-path"
    for allowed in "${allow_paths[@]}"; do
        valid_relative_path "$allowed" || die "invalid allowed path: $allowed"
        bootstrap_path_allowed "$allowed" ||
            die "current bootstrap dispatch permits documentation paths only: $allowed"
    done
fi

command -v git >/dev/null 2>&1 || die 'git executable not found'
command -v sha256sum >/dev/null 2>&1 || die 'sha256sum executable not found'
command -v realpath >/dev/null 2>&1 || die 'realpath executable not found'
command -v timeout >/dev/null 2>&1 || die 'timeout executable not found'
command -v date >/dev/null 2>&1 || die 'date executable not found'
repo_root=$(canonical_dir "$repo_root")
set_safe_directories "$repo_root"
git_top=$(git -C "$repo_root" rev-parse --show-toplevel 2>/dev/null) || die '--repo-root is not a Git worktree'
git_top=$(canonical_dir "$git_top")
[[ "$git_top" == "$repo_root" ]] || die '--repo-root must name the repository root'
[[ "$work_root" != / ]] || die 'refusing to use / as the work root'
work_root=$(realpath -m -- "$work_root")
[[ "$work_root" != "$repo_root" && "$work_root" != "$repo_root"/* && "$repo_root" != "$work_root"/* ]] ||
    die 'work root and repository must not overlap'
mkdir -p -- "$work_root"
work_root=$(canonical_dir "$work_root")

base_commit=$(git -C "$repo_root" rev-parse --verify "$base_ref^{commit}" 2>/dev/null) || die 'base commit unavailable'
[[ "$base_commit" == "${base_ref,,}" ]] || die 'base ref did not resolve exactly'
coordinator_head=$(git -C "$repo_root" rev-parse --verify HEAD^{commit}) || die 'unable to resolve coordinator HEAD'
[[ "$coordinator_head" == "$base_commit" ]] ||
    die 'coordinator HEAD must equal the supplied base commit'
[[ -z "$(git -C "$repo_root" status --porcelain=v1 --untracked-files=all)" ]] ||
    die 'coordinator repository must be clean before dispatch'
if [[ "$mode" != smoke ]]; then
    task_spec_is_approved_at "$repo_root" "$base_commit" "$task_spec" ||
        die 'task spec must be a nonempty approved file committed at the base revision'
fi

script_dir=$(canonical_dir "$(dirname -- "${BASH_SOURCE[0]}")")
[[ "$script_dir" == "$repo_root/scripts" ]] || die 'dispatcher must run from the supplied repository root'
policy_files=(
    scripts/forge-dispatch.sh
    scripts/create-worktree.sh
    scripts/run-codex.sh
    scripts/run-claude.sh
    scripts/verify-candidate.sh
    scripts/test-forge-dispatch.sh
)
declare -a policy_blobs=()
for policy_file in "${policy_files[@]}"; do
    helper=${policy_file#scripts/}
    [[ -x "$repo_root/$policy_file" && ! -L "$repo_root/$policy_file" ]] ||
        die "required policy/helper is missing, non-executable, or a symlink: $policy_file"
    tree_entry=$(git -C "$repo_root" ls-tree "$base_commit" -- "$policy_file")
    [[ "$(awk '{print $1}' <<<"$tree_entry")" == 100755 ]] ||
        die "policy/helper is not executable at the base commit: $policy_file"
    expected_blob=$(git -C "$repo_root" rev-parse "$base_commit:$policy_file") ||
        die "policy/helper is missing at the base commit: $policy_file"
    actual_blob=$(git -C "$repo_root" hash-object --no-filters -- "$repo_root/$policy_file") ||
        die "unable to hash policy/helper: $policy_file"
    [[ "$actual_blob" == "$expected_blob" ]] ||
        die "policy/helper differs from the authenticated base commit: $policy_file"
    policy_blobs+=("$actual_blob")
done

mkdir -p -- "$work_root/evidence"
evidence_parent=$(canonical_dir "$work_root/evidence")
evidence_dir="$evidence_parent/$job_id"
[[ "$evidence_dir" == "$evidence_parent"/* ]] || die 'derived evidence path escaped the work root'
[[ ! -e "$evidence_dir" && ! -L "$evidence_dir" ]] || die "evidence path already exists: $evidence_dir"
mkdir -- "$evidence_dir"

worktree_path=''
cleanup_worktree=false
dispatch_started_epoch=$(date +%s)
dispatch_started_at=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

write_checksums() {
    (
        cd -- "$evidence_dir"
        find . -maxdepth 1 -type f ! -name SHA256SUMS -printf '%P\n' |
            sort |
            while IFS= read -r evidence_file; do
                [[ -n "$evidence_file" ]] && sha256sum "$evidence_file"
            done
    ) >"$evidence_dir/SHA256SUMS"
}

write_result() {
    local result_status=$1
    local cleanup_result=$2
    local checksum_status=$3
    local finished_epoch finished_at duration

    finished_epoch=$(date +%s)
    finished_at=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    duration=$((finished_epoch - dispatch_started_epoch))
    ((duration >= 0)) || duration=0
    {
        if ((result_status == 0)); then
            printf 'result=pass\n'
        else
            printf 'result=fail\n'
        fi
        printf 'exit_code=%s\n' "$result_status"
        printf 'worktree=%s\n' "$cleanup_result"
        printf 'checksum=%s\n' "$checksum_status"
        printf 'started_at=%s\n' "$dispatch_started_at"
        printf 'finished_at=%s\n' "$finished_at"
        printf 'duration_seconds=%s\n' "$duration"
    } >"$evidence_dir/dispatch-result.env"
}

finish() {
    local status=$?
    local cleanup_result=not-created
    trap - EXIT

    if [[ -n "$worktree_path" ]]; then
        if [[ "$cleanup_worktree" == true ]]; then
            if timeout --signal=TERM --kill-after=5s 60 \
                git -C "$repo_root" -c core.hooksPath=/dev/null -c core.fsmonitor=false \
                    worktree remove "$worktree_path"; then
                cleanup_result=removed
            else
                cleanup_result=failed
                status=1
            fi
        else
            cleanup_result=retained
        fi
    fi

    write_result "$status" "$cleanup_result" pending
    if ! write_checksums; then
        status=1
        rm -f -- "$evidence_dir/SHA256SUMS"
        write_result "$status" "$cleanup_result" failed
        exit "$status"
    fi
    write_result "$status" "$cleanup_result" pass
    if ! write_checksums; then
        status=1
        rm -f -- "$evidence_dir/SHA256SUMS"
        write_result "$status" "$cleanup_result" failed
        exit "$status"
    fi
    exit "$status"
}
trap finish EXIT

{
    printf 'schema=vision-forge-dispatch-v1\n'
    printf 'job_id=%s\n' "$job_id"
    printf 'mode=%s\n' "$mode"
    printf 'agent=%s\n' "$agent"
    printf 'base_commit=%s\n' "$base_commit"
    printf 'policy_commit=%s\n' "$base_commit"
    printf 'timeout_seconds=%s\n' "$timeout_seconds"
    printf 'started_at=%s\n' "$dispatch_started_at"
    printf 'check=gate-f-structural-only\n'
    if [[ "$mode" != smoke ]]; then
        printf 'task_id=%s\n' "$task_id"
        printf 'task_spec=%s\n' "$task_spec"
        printf 'branch=task/%s-%s\n' "$task_id" "$slug"
    fi
} >"$evidence_dir/dispatch-manifest.env"

{
    printf 'policy_commit=%s\n' "$base_commit"
    for index in "${!policy_files[@]}"; do
        printf '%s=%s\n' "${policy_files[$index]}" "${policy_blobs[$index]}"
    done
} >"$evidence_dir/policy-integrity.env"

{
    uname -srm
    git --version
    bash --version | sed -n '1p'
} >"$evidence_dir/environment.txt"

if [[ "$mode" != smoke ]]; then
    printf '%s\n' "${allow_paths[@]}" | sort -u >"$evidence_dir/dispatch-allowed-paths.txt"
fi

create_args=(
    --repo-root "$repo_root"
    --work-root "$work_root"
    --job-id "$job_id"
    --base-ref "$base_commit"
)
cleanup_worktree=true
expected_worktree="$work_root/worktrees/$job_id"
set +e
created_output=$(timeout --signal=TERM --kill-after=5s 60 \
    "$script_dir/create-worktree.sh" "${create_args[@]}" 2>"$evidence_dir/create-worktree.stderr.txt")
create_status=$?
set -e
if ((create_status != 0)); then
    [[ -d "$expected_worktree" ]] && worktree_path=$expected_worktree
    die "worktree creation failed with status $create_status"
fi
worktree_path=$created_output
[[ "$worktree_path" == "$expected_worktree" ]] || die 'worktree helper returned an unexpected path'

if [[ "$mode" == smoke ]]; then
    timeout --signal=TERM --kill-after=5s 60 \
        "$script_dir/verify-candidate.sh" \
        --repo-root "$repo_root" \
        --work-root "$work_root" \
        --job-id "$job_id" \
        --base-ref "$base_commit" \
        --profile smoke >"$evidence_dir/verification-output.txt" 2>"$evidence_dir/verification-stderr.txt"
else
    runner_args=(
        --work-root "$work_root"
        --job-id "$job_id"
        --base-ref "$base_commit"
        --task-spec "$task_spec"
        --mode "$mode"
        --timeout-seconds "$timeout_seconds"
    )
    for allowed in "${allow_paths[@]}"; do
        runner_args+=(--allow-path "$allowed")
    done

    timeout --signal=TERM --kill-after=5s "$timeout_seconds" \
        "$script_dir/run-$agent.sh" "${runner_args[@]}" \
        >"$evidence_dir/agent-wrapper-output.txt" 2>"$evidence_dir/agent-wrapper-stderr.txt"

    verify_args=(
        --repo-root "$repo_root"
        --work-root "$work_root"
        --job-id "$job_id"
        --base-ref "$base_commit"
    )
    if [[ "$mode" == dry-run ]]; then
        verify_args+=(--profile smoke)
    else
        verify_args+=(--profile candidate --branch "task/$task_id-$slug" --task-spec "$task_spec")
        for allowed in "${allow_paths[@]}"; do
            verify_args+=(--allow-path "$allowed")
        done
    fi
    timeout --signal=TERM --kill-after=5s 60 \
        "$script_dir/verify-candidate.sh" "${verify_args[@]}" \
        >"$evidence_dir/verification-output.txt" 2>"$evidence_dir/verification-stderr.txt"
fi

printf 'FORGE dispatch %s passed; evidence: %s\n' "$mode" "$evidence_dir"
