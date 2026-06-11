#!/bin/bash
# Block mutating Terraform commands in day-2 operational repos.
input=$(cat)
command=$(printf '%s' "$input" | python3 -c "import sys, json; print(json.load(sys.stdin).get('command', ''))" 2>/dev/null)

if [[ -z "$command" ]]; then
  echo '{"permission":"allow"}'
  exit 0
fi

if echo "$command" | grep -qE 'terraform(\s|$).*(-auto-approve|--auto-approve)'; then
  echo '{
    "permission": "deny",
    "user_message": "Terraform -auto-approve is blocked in the day-2 ops workspace. Open bootstrap.code-workspace for DR-only changes.",
    "agent_message": "Terraform auto-approve is forbidden in this operational workspace."
  }'
  exit 0
fi

if echo "$command" | grep -qE 'terraform(\s|$).*\b(apply|destroy|import|taint|untaint)\b'; then
  echo '{
    "permission": "deny",
    "user_message": "Terraform apply/destroy is blocked in the day-2 ops workspace. Open bootstrap.code-workspace for DR-only changes.",
    "agent_message": "Terraform mutating commands are forbidden in this operational workspace."
  }'
  exit 0
fi

if echo "$command" | grep -qE 'terraform(\s|$).*state\s+(rm|push|mv)\b'; then
  echo '{
    "permission": "deny",
    "user_message": "Terraform state mutations are blocked in the day-2 ops workspace. Open bootstrap.code-workspace for DR-only changes.",
    "agent_message": "Terraform state mutation commands are forbidden in this operational workspace."
  }'
  exit 0
fi

echo '{"permission":"allow"}'
exit 0
