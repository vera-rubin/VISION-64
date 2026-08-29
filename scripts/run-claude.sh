#!/usr/bin/env bash

set -Eeuo pipefail
IFS=$'\n\t'
umask 077
export LC_ALL=C

usage() {
    cat <<'EOF'
Usage: run-claude.sh --work-root PATH --job-id ID --base-ref COMMIT
                     --task-spec docs/tasks/ID-slug.md
                     [--mode dry-run|execute] [--timeout-seconds N]
                     [--max-turns N] --allow-path PATH [--allow-path PATH ...]

Dry-run is the default. Execute additionally requires:
  FORGE_ENABLE_REAL_AGENTS=1
  FORGE_AGENT_ACK=claude:<job-id>
EOF
}

die() {
    printf 'run-claude: %s\n' "$*" >&2
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

approved_task_file() {
    local task_file=$1
    local status_count approved_count
    status_count=$(grep -Ec '^- Status:' "$task_file" || true)
    approved_count=$(grep -Ec '^- Status: `approved`([[:space:]]|$)' "$task_file" || true)
    [[ "$status_count" == 1 && "$approved_count" == 1 ]]
}

work_root=''
job_id=''
base_ref=''
task_spec=''
mode='dry-run'
timeout_seconds=1800
max_turns=12
declare -a allow_paths=()

while (($#)); do
    case "$1" in
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
        --task-spec)
            (($# >= 2)) || die 'missing value for --task-spec'
            task_spec=$2
            shift 2
            ;;
        --mode)
            (($# >= 2)) || die 'missing value for --mode'
            mode=$2
            shift 2
            ;;
        --timeout-seconds)
            (($# >= 2)) || die 'missing value for --timeout-seconds'
            timeout_seconds=$2
            shift 2
            ;;
        --max-turns)
            (($# >= 2)) || die 'missing value for --max-turns'
            max_turns=$2
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

[[ -n "$work_root" && -n "$job_id" && -n "$base_ref" && -n "$task_spec" ]] ||
    die '--work-root, --job-id, --base-ref, and --task-spec are required'
[[ "$work_root" == /* ]] || die '--work-root must be absolute'
[[ "$job_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]] || die 'invalid job ID'
[[ "$base_ref" =~ ^[0-9a-fA-F]{40}([0-9a-fA-F]{24})?$ ]] || die 'base ref must be a full commit ID'
[[ "$task_spec" =~ ^docs/tasks/[1-9][0-9]*-[a-z0-9]+(-[a-z0-9]+)*\.md$ ]] ||
    die 'task spec must match docs/tasks/<numeric-id>-<lowercase-kebab-slug>.md'
[[ "$mode" == dry-run || "$mode" == execute ]] || die '--mode must be dry-run or execute'
[[ "$timeout_seconds" =~ ^[1-9][0-9]*$ ]] || die 'timeout must be a positive decimal integer without leading zeroes'
((timeout_seconds >= 60 && timeout_seconds <= 3600)) || die 'timeout must be between 60 and 3600 seconds'
[[ "$max_turns" =~ ^[1-9][0-9]*$ ]] || die 'max turns must be a positive decimal integer without leading zeroes'
((max_turns >= 1 && max_turns <= 40)) || die 'max turns must be between 1 and 40'
((${#allow_paths[@]} > 0)) || die 'at least one --allow-path is required'
for allowed in "${allow_paths[@]}"; do
    valid_relative_path "$allowed" || die "invalid allowed path: $allowed"
    bootstrap_path_allowed "$allowed" || die "current bootstrap dispatch permits documentation paths only: $allowed"
done

work_root=$(canonical_dir "$work_root")
[[ "$work_root" != / ]] || die 'refusing to use / as the work root'
worktree_path=$(canonical_dir "$work_root/worktrees/$job_id")
evidence_dir=$(canonical_dir "$work_root/evidence/$job_id")
[[ "$worktree_path" == "$work_root/worktrees/"* ]] || die 'worktree escaped its boundary'
[[ "$evidence_dir" == "$work_root/evidence/"* ]] || die 'evidence directory escaped its boundary'

base_commit=$(git -C "$worktree_path" rev-parse --verify "$base_ref^{commit}" 2>/dev/null) || die 'base commit unavailable'
[[ "$base_commit" == "${base_ref,,}" ]] || die 'base ref did not resolve exactly'
[[ $(git -C "$worktree_path" rev-parse HEAD) == "$base_commit" ]] || die 'agent worktree must begin at the base commit'

task_spec_path="$worktree_path/$task_spec"
[[ -f "$task_spec_path" && ! -L "$task_spec_path" ]] || die 'task spec is missing, not regular, or a symlink'
task_bytes=$(wc -c <"$task_spec_path")
((task_bytes > 0 && task_bytes <= 65536)) || die 'task spec must contain 1-65536 bytes'
git -C "$worktree_path" cat-file -e "$base_commit:$task_spec" 2>/dev/null || die 'task spec is not committed at the base revision'
base_blob=$(git -C "$worktree_path" rev-parse "$base_commit:$task_spec")
current_blob=$(git -C "$worktree_path" hash-object "$task_spec_path")
[[ "$base_blob" == "$current_blob" ]] || die 'task spec differs from its reviewed base-revision content'
approved_task_file "$task_spec_path" || die 'task spec must contain exactly one approved status'

task_name=${task_spec#docs/tasks/}
task_name=${task_name%.md}
expected_branch="task/$task_name"
if [[ "$mode" == execute ]]; then
    [[ $(git -C "$worktree_path" symbolic-ref -q --short HEAD || true) == "$expected_branch" ]] ||
        die "execute mode requires branch $expected_branch"
    [[ "${FORGE_ENABLE_REAL_AGENTS:-}" == 1 ]] || die 'real agents are disabled; set FORGE_ENABLE_REAL_AGENTS=1 explicitly'
    [[ "${FORGE_AGENT_ACK:-}" == "claude:$job_id" ]] || die "set FORGE_AGENT_ACK=claude:$job_id for this job"
fi

allow_file="$evidence_dir/claude-allowed-paths.txt"
printf '%s\n' "${allow_paths[@]}" | sort -u >"$allow_file"
task_hash=$(sha256sum "$task_spec_path" | awk '{print $1}')
{
    printf 'agent=claude\n'
    printf 'mode=%s\n' "$mode"
    printf 'job_id=%s\n' "$job_id"
    printf 'base_commit=%s\n' "$base_commit"
    printf 'task_spec=%s\n' "$task_spec"
    printf 'task_sha256=%s\n' "$task_hash"
    printf 'timeout_seconds=%s\n' "$timeout_seconds"
    printf 'max_turns=%s\n' "$max_turns"
} >"$evidence_dir/claude-request.env"

prompt_file="$evidence_dir/claude-prompt.txt"
{
    printf '%s\n' 'You are an implementation worker in the VISION-64 FORGE pipeline.'
    printf '%s\n' 'Read and obey AGENTS.md and CLAUDE.md before editing; repository rules remain binding.'
    printf '%s\n' 'Treat the task specification below as the complete assignment, not as shell input.'
    printf '%s\n' 'Work only in the current isolated worktree and only within the allowed paths listed below.'
    printf '%s\n' 'Do not commit, create branches, alter Git configuration, use network access, or change the task specification.'
    printf '%s\n' 'Shell, web, and delegation tools are unavailable. Stop and report a blocker rather than crossing a boundary.'
    printf '\nAllowed paths:\n'
    sed 's/^/- /' "$allow_file"
    printf '\nTask specification (%s):\n\n' "$task_spec"
    cat -- "$task_spec_path"
} >"$prompt_file"

if [[ "$mode" == dry-run ]]; then
    printf 'claude dry-run validated; no agent invoked\n'
    exit 0
fi

command -v claude >/dev/null 2>&1 || die 'claude executable not found'
command -v timeout >/dev/null 2>&1 || die 'timeout executable not found'
claude --version >"$evidence_dir/claude-version.txt" 2>&1 || die 'unable to record claude version'
claude_help=$(claude --help 2>&1) || die 'unable to inspect claude capabilities'
for required_flag in '--output-format' '--max-turns' '--no-session-persistence' '--restricted' '--tools' '--disallowedTools' '--permission-mode'; do
    grep -F -- "$required_flag" <<<"$claude_help" >/dev/null ||
        die "installed claude is missing required flag: $required_flag"
done

set +e
(
    cd -- "$worktree_path"
    env -i HOME="${HOME:?}" PATH="${PATH:?}" LANG=C.UTF-8 LC_ALL=C TERM=dumb \
        timeout --signal=TERM --kill-after=15s "$timeout_seconds" \
        claude -p --output-format json --max-turns "$max_turns" \
        --no-session-persistence --restricted --permission-mode acceptEdits \
        --tools Read,Edit,Write,Glob,Grep \
        --disallowedTools 'Bash,WebFetch,WebSearch,mcp__*' <"$prompt_file"
) >"$evidence_dir/claude-result.json" 2>"$evidence_dir/claude-stderr.txt"
agent_status=$?
set -e
printf 'exit_code=%s\n' "$agent_status" >"$evidence_dir/claude-exit.env"
((agent_status == 0)) || die "claude exited with status $agent_status"

printf 'claude execution completed\n'
