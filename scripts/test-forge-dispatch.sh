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

die() {
    printf 'test-forge-dispatch: %s\n' "$*" >&2
    exit 1
}

expect_failure() {
    local label=$1
    shift
    if "$@" >"$test_root/$label.stdout" 2>"$test_root/$label.stderr"; then
        die "negative case unexpectedly succeeded: $label"
    fi
    printf 'ok - rejects %s\n' "$label"
}

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
repo_root=$(cd -- "$script_dir/.." && pwd -P)
git_top=$(git -C "$repo_root" rev-parse --show-toplevel)
git_top=$(cd -- "$git_top" && pwd -P)
[[ "$git_top" == "$repo_root" ]] || die 'test must run from the VISION-64 checkout'
set_safe_directories "$repo_root"

temporary_parent=$(cd -- "${TMPDIR:-/tmp}" && pwd -P)
test_root=$(mktemp -d "$temporary_parent/vision-forge-test.XXXXXX")
test_root=$(cd -- "$test_root" && pwd -P)
[[ "$test_root" == "$temporary_parent"/vision-forge-test.* ]] || die 'temporary directory escaped its parent'

cleanup() {
    local status=$?
    trap - EXIT
    if [[ "$test_root" == "$temporary_parent"/vision-forge-test.* && -d "$test_root" ]]; then
        rm -rf -- "$test_root"
    fi
    exit "$status"
}
trap cleanup EXIT

base_commit=$(git -C "$repo_root" rev-parse HEAD)
status_before=$(git -C "$repo_root" status --porcelain=v1 --untracked-files=all)
branches_before=$(git -C "$repo_root" for-each-ref --format='%(refname)' refs/heads/)
worktrees_before=$(git -C "$repo_root" worktree list --porcelain)
work_root="$test_root/forge"
job_id=local-smoke

"$script_dir/forge-dispatch.sh" \
    --repo-root "$repo_root" \
    --work-root "$work_root" \
    --job-id "$job_id" \
    --base-ref "$base_commit" \
    --mode smoke \
    --agent none >"$test_root/smoke.stdout"

evidence_dir="$work_root/evidence/$job_id"
for evidence_file in \
    dispatch-manifest.env environment.txt create-worktree.stderr.txt git-status.txt candidate.patch \
    changed-paths.txt diff-check.txt verification.env verification-output.txt policy-integrity.env \
    verification-stderr.txt dispatch-result.env SHA256SUMS; do
    [[ -f "$evidence_dir/$evidence_file" ]] || die "missing smoke evidence: $evidence_file"
done
[[ ! -e "$work_root/worktrees/$job_id" ]] || die 'smoke worktree was not removed'
[[ ! -s "$evidence_dir/git-status.txt" ]] || die 'smoke status evidence is not clean'
[[ ! -s "$evidence_dir/candidate.patch" ]] || die 'smoke patch evidence is not empty'
[[ ! -s "$evidence_dir/changed-paths.txt" ]] || die 'smoke changed-path evidence is not empty'
grep -Fx 'mode=smoke' "$evidence_dir/dispatch-manifest.env" >/dev/null || die 'smoke mode evidence missing'
grep -Fx 'agent=none' "$evidence_dir/dispatch-manifest.env" >/dev/null || die 'agentless evidence missing'
grep -Fx 'head_state=detached' "$evidence_dir/verification.env" >/dev/null || die 'detached evidence missing'
grep -Fx 'check=structural-only' "$evidence_dir/verification.env" >/dev/null || die 'structural-only evidence missing'
grep -Fx 'checksum=pass' "$evidence_dir/dispatch-result.env" >/dev/null || die 'checksum result missing'
grep -Fx 'result=pass' "$evidence_dir/dispatch-result.env" >/dev/null || die 'pass evidence missing'
grep -Fx 'worktree=removed' "$evidence_dir/dispatch-result.env" >/dev/null || die 'cleanup evidence missing'
(cd -- "$evidence_dir" && sha256sum -c SHA256SUMS >/dev/null) || die 'evidence checksum verification failed'
printf 'ok - detached agentless smoke\n'

expect_failure invalid-job \
    "$script_dir/forge-dispatch.sh" --repo-root "$repo_root" --work-root "$test_root/invalid-job" \
    --job-id '../escape' --base-ref "$base_commit"
expect_failure symbolic-ref \
    "$script_dir/forge-dispatch.sh" --repo-root "$repo_root" --work-root "$test_root/symbolic-ref" \
    --job-id symbolic-ref --base-ref HEAD
expect_failure overlapping-root \
    "$script_dir/forge-dispatch.sh" --repo-root "$repo_root" --work-root "$repo_root" \
    --job-id overlap --base-ref "$base_commit"
expect_failure smoke-agent \
    "$script_dir/forge-dispatch.sh" --repo-root "$repo_root" --work-root "$test_root/smoke-agent" \
    --job-id smoke-agent --base-ref "$base_commit" --mode smoke --agent codex
expect_failure traversal-allowance \
    "$script_dir/forge-dispatch.sh" --repo-root "$repo_root" --work-root "$test_root/traversal" \
    --job-id traversal --base-ref "$base_commit" --mode dry-run --agent codex \
    --task-id 1 --slug document-smoke --task-spec docs/tasks/1-document-smoke.md \
    --allow-path ../kernel
expect_failure kernel-path \
    "$script_dir/forge-dispatch.sh" --repo-root "$repo_root" --work-root "$test_root/kernel-path" \
    --job-id kernel-path --base-ref "$base_commit" --mode dry-run --agent codex \
    --task-id 1 --slug document-smoke --task-spec docs/tasks/1-document-smoke.md \
    --allow-path kernel/
missing_task_root="$test_root/missing-task"
expect_failure missing-task \
    "$script_dir/forge-dispatch.sh" --repo-root "$repo_root" --work-root "$missing_task_root" \
    --job-id missing-task --base-ref "$base_commit" --mode dry-run --agent codex \
    --task-id 1 --slug document-smoke --task-spec docs/tasks/1-document-smoke.md \
    --allow-path docs/
[[ ! -e "$missing_task_root/worktrees" ]] || die 'missing task created a worktree root'
expect_failure unknown-command \
    "$script_dir/forge-dispatch.sh" --repo-root "$repo_root" --work-root "$test_root/command" \
    --job-id command --base-ref "$base_commit" --command 'echo unsafe'
expect_failure absent-execute-gates \
    env -u FORGE_ENABLE_REAL_AGENTS -u FORGE_AGENT_ACK \
    "$script_dir/forge-dispatch.sh" --repo-root "$repo_root" --work-root "$test_root/execute" \
    --job-id execute --base-ref "$base_commit" --mode execute --agent codex \
    --task-id 1 --slug document-smoke --task-spec docs/tasks/1-document-smoke.md \
    --allow-path docs/
expect_failure evidence-replay \
    "$script_dir/forge-dispatch.sh" --repo-root "$repo_root" --work-root "$work_root" \
    --job-id "$job_id" --base-ref "$base_commit" --mode smoke --agent none

env GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0="$test_root/unsafe-hooks" \
    "$script_dir/forge-dispatch.sh" --repo-root "$repo_root" --work-root "$test_root/injected-config" \
    --job-id injected-config --base-ref "$base_commit" --mode smoke --agent none >"$test_root/injected-config.stdout"
grep -F 'FORGE dispatch smoke passed' "$test_root/injected-config.stdout" >/dev/null ||
    die 'injected Git configuration altered the smoke dispatch'
printf 'ok - caller Git configuration is ignored\n'

fixture_repo="$test_root/fixture-repo"
fixture_work_root="$test_root/fixture-work"
set_safe_directories "$repo_root" "$fixture_repo"
git init -q -b main "$fixture_repo"
git -C "$fixture_repo" config user.name 'VISION test'
git -C "$fixture_repo" config user.email 'vision-test@example.invalid'
git -C "$fixture_repo" config core.autocrlf false
mkdir -p "$fixture_repo/docs/tasks"
printf '# Task 1: Documentation fixture\n\n- Schema: `vision-task-v1`\n- Status: `approved`\n' \
    >"$fixture_repo/docs/tasks/1-document-fixture.md"
git -C "$fixture_repo" add docs/tasks/1-document-fixture.md
git -C "$fixture_repo" commit -q -m 'test: add approved task fixture'
fixture_base=$(git -C "$fixture_repo" rev-parse HEAD)

replacement_repo="$test_root/replacement-repo"
git clone -q "$fixture_repo" "$replacement_repo"
set_safe_directories "$repo_root" "$fixture_repo" "$replacement_repo"
git -C "$replacement_repo" config user.name 'VISION replacement test'
git -C "$replacement_repo" config user.email 'vision-replacement@example.invalid'
replacement_commit=$(git -C "$replacement_repo" rev-parse HEAD)
printf '# replacement object\n' >"$replacement_repo/docs/tasks/1-document-fixture.md"
git -C "$replacement_repo" add docs/tasks/1-document-fixture.md
git -C "$replacement_repo" commit -q -m 'test: replacement object'
replacement_target=$(git -C "$replacement_repo" rev-parse HEAD)
git -C "$replacement_repo" replace "$replacement_commit" "$replacement_target"
replacement_work_root="$test_root/replacement-work"
replacement_worktree=$(
    GIT_NO_REPLACE_OBJECTS=0 "$script_dir/create-worktree.sh" \
        --repo-root "$replacement_repo" \
        --work-root "$replacement_work_root" \
        --job-id replacement \
        --base-ref "$replacement_commit" 2>"$test_root/replacement-create.stderr"
)
grep -F '# Task 1: Documentation fixture' "$replacement_worktree/docs/tasks/1-document-fixture.md" >/dev/null ||
    die 'replacement refs changed the selected base object'
! grep -F '# replacement object' "$replacement_worktree/docs/tasks/1-document-fixture.md" >/dev/null ||
    die 'replacement object was unexpectedly visible'
git -C "$replacement_repo" replace -d "$replacement_commit" >/dev/null

fixture_job=candidate-fixture
fixture_worktree=$(
    "$script_dir/create-worktree.sh" \
        --repo-root "$fixture_repo" \
        --work-root "$fixture_work_root" \
        --job-id "$fixture_job" \
        --base-ref "$fixture_base" \
        --branch task/1-document-fixture 2>"$test_root/fixture-create.stderr"
)
mkdir -p "$fixture_work_root/evidence/$fixture_job"
printf 'untracked candidate evidence\n' >"$fixture_worktree/docs/new.md"
"$script_dir/verify-candidate.sh" \
    --repo-root "$fixture_repo" \
    --work-root "$fixture_work_root" \
    --job-id "$fixture_job" \
    --base-ref "$fixture_base" \
    --profile candidate \
    --branch task/1-document-fixture \
    --task-spec docs/tasks/1-document-fixture.md \
    --allow-path docs/ >"$test_root/fixture-verify.stdout"
grep -F 'untracked candidate evidence' \
    "$fixture_work_root/evidence/$fixture_job/candidate.patch" >/dev/null ||
    die 'candidate patch omitted untracked file content'
grep -Fx 'docs/new.md' \
    "$fixture_work_root/evidence/$fixture_job/changed-paths.txt" >/dev/null ||
    die 'candidate path evidence omitted the untracked file'
dd if=/dev/zero of="$fixture_worktree/docs/too-large.md" bs=1024 count=1025 status=none
expect_failure oversized-file \
    "$script_dir/verify-candidate.sh" \
    --repo-root "$fixture_repo" \
    --work-root "$fixture_work_root" \
    --job-id "$fixture_job" \
    --base-ref "$fixture_base" \
    --profile candidate \
    --branch task/1-document-fixture \
    --task-spec docs/tasks/1-document-fixture.md \
    --allow-path docs/
rm -f -- "$fixture_worktree/docs/too-large.md"
printf '\nunauthorized task change\n' \
    >>"$fixture_worktree/docs/tasks/1-document-fixture.md"
expect_failure changed-task \
    "$script_dir/verify-candidate.sh" \
    --repo-root "$fixture_repo" \
    --work-root "$fixture_work_root" \
    --job-id "$fixture_job" \
    --base-ref "$fixture_base" \
    --profile candidate \
    --branch task/1-document-fixture \
    --task-spec docs/tasks/1-document-fixture.md \
    --allow-path docs/
printf 'ok - candidate evidence captures untracked files and protects task authority\n'

status_after=$(git -C "$repo_root" status --porcelain=v1 --untracked-files=all)
branches_after=$(git -C "$repo_root" for-each-ref --format='%(refname)' refs/heads/)
worktrees_after=$(git -C "$repo_root" worktree list --porcelain)
[[ "$status_after" == "$status_before" ]] || die 'test changed repository status'
[[ "$branches_after" == "$branches_before" ]] || die 'test created or changed a local branch'
[[ "$worktrees_after" == "$worktrees_before" ]] || die 'test leaked a registered worktree'

printf 'ok - repository status, branches, and worktree registry preserved\n'
printf 'all forge dispatch tests passed\n'
